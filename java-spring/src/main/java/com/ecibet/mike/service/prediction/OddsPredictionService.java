package com.ecibet.mike.service.prediction;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import com.ecibet.mike.model.mongodb.MatchContext;
import com.ecibet.mike.repository.MatchContextRepository;
import com.ecibet.mike.service.publisher.OddsPublisher;
import com.ecibet.mike.service.python.PythonClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
@RequiredArgsConstructor
public class OddsPredictionService {

    private final PythonClient pythonClient;
    private final OddsPublisher oddsPublisher;
    private final MatchContextRepository matchContextRepository;
    private final EnsemblePredictor ensemblePredictor;
    private final FallbackOddsService fallbackOddsService;

    private final Map<String, MatchContext> activeMatches = new ConcurrentHashMap<>();

    public void processEvent(MatchEventDTO event, boolean needGPTFeatures) {
        String eventId = event.getEventId();

        MatchContext context = activeMatches.computeIfAbsent(eventId, k -> {
            return matchContextRepository.findByEventId(eventId)
                    .orElse(MatchContext.builder()
                            .eventId(eventId)
                            .externalId(event.getExternalId())
                            .homeTeam(event.getHomeTeam())
                            .awayTeam(event.getAwayTeam())
                            .createdAt(Instant.now())
                            .build());
        });

        updateContext(context, event);

        try {
            OddsUpdateEventDTO odds;

            if ("SCHEDULED".equals(event.getEventType())) {
                odds = ensemblePredictor.predictPreMatch(context, needGPTFeatures);
            } else {
                odds = ensemblePredictor.predictLive(context, event, needGPTFeatures);
            }

            oddsPublisher.publish(odds);

            context.setLastOdds(odds);
            context.setLastUpdate(Instant.now());
            matchContextRepository.save(context);

            log.info("Odds publicadas para partido: {}, evento: {}", eventId, event.getEventType());

        } catch (Exception e) {
            log.error("Error generando odds para partido: {}", eventId, e);
            OddsUpdateEventDTO fallbackOdds = fallbackOddsService.getFallbackOdds(event);
            oddsPublisher.publish(fallbackOdds);
        }
    }

    private void updateContext(MatchContext context, MatchEventDTO event) {
        context.setMinute(event.getMinute());
        context.setHomeScore(event.getHomeScore());
        context.setAwayScore(event.getAwayScore());
        context.setStatus(event.getStatus());

        if (context.getEventHistory() == null) {
            context.setEventHistory(new java.util.ArrayList<>());
        }

        if (event.getEventType() != null && !"MINUTE_UPDATE".equals(event.getEventType())) {
            context.getEventHistory().add(event);
        }
    }

    public OddsUpdateEventDTO forcePrediction(String eventId, boolean useGptFeatures) {
        MatchContext context = activeMatches.get(eventId);
        if (context == null) {
            throw new IllegalArgumentException("Partido no encontrado: " + eventId);
        }

        try {
            OddsUpdateEventDTO odds = ensemblePredictor.predictPreMatch(context, useGptFeatures);
            oddsPublisher.publish(odds);
            return odds;
        } catch (Exception e) {
            log.error("Error en forcePrediction: {}", eventId, e);
            return fallbackOddsService.getFallbackOddsForContext(context);
        }
    }
}