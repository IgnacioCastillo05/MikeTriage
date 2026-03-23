package com.ecibet.mike.model.mongodb;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "historical_matches")
public class HistoricalMatch {

    @Id
    private String id;

    @Indexed(unique = true)
    private String externalId;

    private String homeTeam;
    private String awayTeam;
    private String homeTeamId;
    private String awayTeamId;

    private Integer homeScore;
    private Integer awayScore;

    private String competition;
    private String competitionId;
    private String season;
    private String round;

    private LocalDate matchDate;
    private String status;
    private String matchType;

    private Integer homePossession;
    private Integer awayPossession;
    private Integer homeShotsOnTarget;
    private Integer awayShotsOnTarget;
    private Integer homeShotsOffTarget;
    private Integer awayShotsOffTarget;
    private Integer homeCorners;
    private Integer awayCorners;
    private Integer homeFouls;
    private Integer awayFouls;
    private Integer homeYellowCards;
    private Integer awayYellowCards;
    private Integer homeRedCards;
    private Integer awayRedCards;

    private List<Map<String, Object>> timeline;

    private Map<String, Double> historicalOdds;

    private Integer homePosition;
    private String homeForm;
    private Integer homePoints;
    private Integer homePlayed;
    private Integer homeWins;
    private Integer homeDraws;
    private Integer homeLosses;
    private Integer homeGoalsFor;
    private Integer homeGoalsAgainst;
    private Integer homeGoalDifference;

    private LocalDateTime syncedAt;
    private String syncVersion;
    private String syncStatus;

    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;
}