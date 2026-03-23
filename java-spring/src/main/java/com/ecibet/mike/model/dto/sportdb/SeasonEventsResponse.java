package com.ecibet.mike.model.dto.sportdb;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class SeasonEventsResponse {

    @JsonProperty("events")
    private List<EventEntry> events;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class EventEntry {

        @JsonProperty("idEvent")
        private String idEvent;

        @JsonProperty("idSoccerXML")
        private String idSoccerXML;

        @JsonProperty("idAPIfootball")
        private String idAPIfootball;

        @JsonProperty("strEvent")
        private String strEvent;

        @JsonProperty("strEventAlternate")
        private String strEventAlternate;

        @JsonProperty("strFilename")
        private String strFilename;

        @JsonProperty("strSport")
        private String strSport;

        @JsonProperty("idLeague")
        private String idLeague;

        @JsonProperty("strLeague")
        private String strLeague;

        @JsonProperty("strSeason")
        private String strSeason;

        @JsonProperty("strDescriptionEN")
        private String strDescriptionEN;

        @JsonProperty("strHomeTeam")
        private String strHomeTeam;

        @JsonProperty("strAwayTeam")
        private String strAwayTeam;

        @JsonProperty("intHomeScore")
        private String intHomeScore;

        @JsonProperty("intAwayScore")
        private String intAwayScore;

        @JsonProperty("intRound")
        private String intRound;

        @JsonProperty("strStatus")
        private String strStatus;

        @JsonProperty("dateEvent")
        private String dateEvent;

        @JsonProperty("dateEventLocal")
        private String dateEventLocal;

        @JsonProperty("strTime")
        private String strTime;

        @JsonProperty("strTimeLocal")
        private String strTimeLocal;

        @JsonProperty("strTimestamp")
        private String strTimestamp;

        @JsonProperty("strVenue")
        private String strVenue;

        @JsonProperty("strCity")
        private String strCity;

        @JsonProperty("strPoster")
        private String strPoster;

        @JsonProperty("strThumb")
        private String strThumb;

        @JsonProperty("strFanart")
        private String strFanart;

        @JsonProperty("strBanner")
        private String strBanner;

        @JsonProperty("strVideo")
        private String strVideo;

        @JsonProperty("strLocked")
        private String strLocked;
    }
}