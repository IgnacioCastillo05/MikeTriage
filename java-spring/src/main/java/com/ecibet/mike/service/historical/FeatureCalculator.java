package com.ecibet.mike.service.historical;

import com.ecibet.mike.model.mongodb.HistoricalMatch;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
public class FeatureCalculator {

    public Map<String, Double> calculateTeamForm(String teamId, String competition, int matchesCount) {
        Map<String, Double> features = new HashMap<>();

        features.put("points_last_5", 0.0);
        features.put("goals_scored_avg", 0.0);
        features.put("goals_conceded_avg", 0.0);
        features.put("wins", 0.0);
        features.put("draws", 0.0);
        features.put("losses", 0.0);

        return features;
    }

    public Map<String, Double> calculateHeadToHead(String homeTeamId, String awayTeamId) {
        Map<String, Double> features = new HashMap<>();

        features.put("home_wins", 0.0);
        features.put("draws", 0.0);
        features.put("away_wins", 0.0);
        features.put("avg_goals", 0.0);

        return features;
    }

    public double calculateHomeAdvantage(String homeTeamId, String competition) {
        return 1.2;
    }

    public Map<String, Double> extractFeatures(HistoricalMatch match) {
        Map<String, Double> features = new HashMap<>();

        features.put("home_goals_avg", (double) match.getHomeScore());
        features.put("away_goals_avg", (double) match.getAwayScore());
        features.put("total_goals", (double) (match.getHomeScore() + match.getAwayScore()));
        features.put("goal_difference", (double) (match.getHomeScore() - match.getAwayScore()));

        return features;
    }
}