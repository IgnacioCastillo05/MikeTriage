package com.ecibet.mike.model.dto.sportdb;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class TeamResponse {

    @JsonProperty("teams")
    private List<TeamEntry> teams;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class TeamEntry {
        @JsonProperty("idTeam")
        private String idTeam;

        @JsonProperty("idLeague")
        private String idLeague;

        @JsonProperty("strTeam")
        private String strTeam;

        @JsonProperty("strTeamShort")
        private String strTeamShort;

        @JsonProperty("strAlternate")
        private String strAlternate;

        @JsonProperty("strSport")
        private String strSport;

        @JsonProperty("strLeague")
        private String strLeague;

        @JsonProperty("strLeague2")
        private String strLeague2;

        @JsonProperty("strLeague3")
        private String strLeague3;

        @JsonProperty("strLeague4")
        private String strLeague4;

        @JsonProperty("strLeague5")
        private String strLeague5;

        @JsonProperty("strLeague6")
        private String strLeague6;

        @JsonProperty("strLeague7")
        private String strLeague7;

        @JsonProperty("strStadium")
        private String strStadium;

        @JsonProperty("strKeywords")
        private String strKeywords;

        @JsonProperty("strStadiumThumb")
        private String strStadiumThumb;

        @JsonProperty("strStadiumLocation")
        private String strStadiumLocation;

        @JsonProperty("intStadiumCapacity")
        private String intStadiumCapacity;

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

        @JsonProperty("strCountry")
        private String strCountry;

        @JsonProperty("strBadge")
        private String strBadge;

        @JsonProperty("strJersey")
        private String strJersey;

        @JsonProperty("strLogo")
        private String strLogo;

        @JsonProperty("strFanart1")
        private String strFanart1;

        @JsonProperty("strFanart2")
        private String strFanart2;

        @JsonProperty("strFanart3")
        private String strFanart3;

        @JsonProperty("strFanart4")
        private String strFanart4;

        @JsonProperty("intFormedYear")
        private String intFormedYear;

        @JsonProperty("dateFirstEvent")
        private String dateFirstEvent;

        @JsonProperty("strGender")
        private String strGender;

        @JsonProperty("strLocked")
        private String strLocked;
    }
}