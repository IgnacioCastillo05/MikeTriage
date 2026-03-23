package com.ecibet.mike.service.prediction;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import com.ecibet.mike.model.mongodb.MatchContext;
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

    public OddsUpdateEventDTO predictPreMatch(MatchContext context, boolean needGPTFeatures) {
        Map<String, Object> request = new HashMap<>();
        request.put("event_id", context.getEventId());
        request.put("external_id", context.getExternalId());
        request.put("home_team", context.getHomeTeam());
        request.put("away_team", context.getAwayTeam());
        request.put("competition", context.getCompetition());
        request.put("home_form", context.getHomeForm());
        request.put("away_form", context.getAwayForm());
        request.put("home_position", context.getHomePosition());
        request.put("away_position", context.getAwayPosition());
        request.put("need_gpt_features", needGPTFeatures);

        return pythonClient.predictPreMatch(request);
    }

    public OddsUpdateEventDTO predictLive(MatchContext context, MatchEventDTO event, boolean needGPTFeatures) {
        Map<String, Object> request = new HashMap<>();
        request.put("event_id", context.getEventId());
        request.put("external_id", context.getExternalId());
        request.put("home_team", context.getHomeTeam());
        request.put("away_team", context.getAwayTeam());
        request.put("minute", event.getMinute());
        request.put("home_score", event.getHomeScore());
        request.put("away_score", event.getAwayScore());
        request.put("event_type", event.getEventType());
        request.put("team", event.getTeam());
        request.put("description", event.getDescription());
        request.put("need_gpt_features", needGPTFeatures);
        request.put("pre_match_features", context.getPreMatchFeatures());

        return pythonClient.predictLive(request);
    }
}