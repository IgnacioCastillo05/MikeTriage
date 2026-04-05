package com.ecibet.mike.service.prediction;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import com.ecibet.mike.service.python.PythonClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class EnsemblePredictor {

    private final PythonClient pythonClient;

    public OddsUpdateEventDTO predictPreMatch(MatchEventDTO event, boolean needGPTFeatures) {
        Map<String, Object> request = new HashMap<>();
        request.put("event_id", event.getEventId());
        request.put("external_id", event.getExternalId());
        request.put("home_team", event.getHomeTeam());
        request.put("away_team", event.getAwayTeam());
        request.put("competition", event.getCompetition());
        request.put("season", event.getSeason());
        request.put("need_gpt_features", needGPTFeatures);

        log.info("Enviando a Python: {} vs {} en {}",
                event.getHomeTeam(), event.getAwayTeam(), event.getCompetition());

        return pythonClient.predictPreMatch(request);
    }

    public OddsUpdateEventDTO predictLive(MatchEventDTO event, boolean needGPTFeatures) {
        Map<String, Object> request = new HashMap<>();
        request.put("event_id", event.getEventId());
        request.put("external_id", event.getExternalId());
        request.put("home_team", event.getHomeTeam());
        request.put("away_team", event.getAwayTeam());
        request.put("minute", event.getMinute());
        request.put("home_score", event.getHomeScore());
        request.put("away_score", event.getAwayScore());
        request.put("event_type", event.getEventType());
        request.put("need_gpt_features", needGPTFeatures);

        log.info("Enviando a Python live: {} vs {} minuto {} - {}:{}",
                event.getHomeTeam(), event.getAwayTeam(),
                event.getMinute(), event.getHomeScore(), event.getAwayScore());

        return pythonClient.predictLive(request);
    }
}