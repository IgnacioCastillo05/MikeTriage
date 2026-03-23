package com.ecibet.mike.model.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class MatchEventDTO {

    @JsonProperty("eventId")
    private String eventId;

    @JsonProperty("externalId")
    private String externalId;

    @JsonProperty("homeTeam")
    private String homeTeam;

    @JsonProperty("awayTeam")
    private String awayTeam;

    @JsonProperty("homeScore")
    private Integer homeScore;

    @JsonProperty("awayScore")
    private Integer awayScore;

    @JsonProperty("minute")
    private Integer minute;

    @JsonProperty("status")
    private String status;

    @JsonProperty("eventType")
    private String eventType;

    @JsonProperty("team")
    private String team;

    @JsonProperty("description")
    private String description;

    @JsonProperty("timestamp")
    private Instant timestamp;
}