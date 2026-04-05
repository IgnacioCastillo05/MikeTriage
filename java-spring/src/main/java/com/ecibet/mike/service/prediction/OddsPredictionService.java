package com.ecibet.mike.service.prediction;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import com.ecibet.mike.service.publisher.OddsPublisher;
import com.ecibet.mike.service.python.PythonClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class OddsPredictionService {

    private final PythonClient pythonClient;
    private final OddsPublisher oddsPublisher;
    private final EnsemblePredictor ensemblePredictor;
    private final FallbackOddsService fallbackOddsService;

    public void processEvent(MatchEventDTO event, boolean needGPTFeatures) {
        String eventId = event.getEventId();
        log.info("Procesando evento: {} para partido: {}", event.getEventType(), eventId);

        try {
            OddsUpdateEventDTO odds;

            if ("SCHEDULED".equals(event.getEventType())) {
                odds = ensemblePredictor.predictPreMatch(event, needGPTFeatures);
            } else {
                odds = ensemblePredictor.predictLive(event, needGPTFeatures);
            }

            oddsPublisher.publish(odds);
            log.info("Odds publicadas para partido: {}, evento: {}", eventId, event.getEventType());

        } catch (Exception e) {
            log.error("Error generando odds para partido: {}", eventId, e);
            OddsUpdateEventDTO fallbackOdds = fallbackOddsService.getFallbackOdds(event);
            oddsPublisher.publish(fallbackOdds);
        }
    }

    public OddsUpdateEventDTO forcePrediction(MatchEventDTO event, boolean useGptFeatures) {
        log.info("Force prediction para: {} vs {}", event.getHomeTeam(), event.getAwayTeam());

        try {
            OddsUpdateEventDTO odds = ensemblePredictor.predictPreMatch(event, useGptFeatures);
            oddsPublisher.publish(odds);
            return odds;
        } catch (Exception e) {
            log.error("Error en forcePrediction: {}", e.getMessage());
            return fallbackOddsService.getFallbackOdds(event);
        }
    }
}