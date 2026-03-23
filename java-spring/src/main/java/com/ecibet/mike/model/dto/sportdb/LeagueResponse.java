package com.ecibet.mike.model.dto.sportdb;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class LeagueResponse {

    @JsonProperty("leagues")
    private List<LeagueEntry> leagues;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class LeagueEntry {
        @JsonProperty("idLeague")
        private String idLeague;

        @JsonProperty("strLeague")
        private String strLeague;

        @JsonProperty("strLeagueAlternate")
        private String strLeagueAlternate;

        @JsonProperty("strSport")
        private String strSport;

        @JsonProperty("strCountry")
        private String strCountry;

        @JsonProperty("strWebsite")
        private String strWebsite;

        @JsonProperty("strFacebook")
        private String strFacebook;

        @JsonProperty("strInstagram")
        private String strInstagram;

        @JsonProperty("strTwitter")
        private String strTwitter;

        @JsonProperty("strYoutube")
        private String strYoutube;

        @JsonProperty("strDescriptionEN")
        private String strDescriptionEN;

        @JsonProperty("strLogo")
        private String strLogo;

        @JsonProperty("strBadge")
        private String strBadge;

        @JsonProperty("strTrophy")
        private String strTrophy;

        @JsonProperty("intFormedYear")
        private String intFormedYear;

        @JsonProperty("strCurrentSeason")
        private String strCurrentSeason;
    }
}