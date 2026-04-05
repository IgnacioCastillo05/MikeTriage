package com.ecibet.mike.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MatchEventDTO {
    private String eventId;
    private String externalId;
    private String homeTeam;
    private String awayTeam;
    private String competition;
    private String season;
    private Integer minute;
    private Integer homeScore;
    private Integer awayScore;
    private String status;
    private String eventType;
    private String team;
    private String description;
    private Instant timestamp;
}