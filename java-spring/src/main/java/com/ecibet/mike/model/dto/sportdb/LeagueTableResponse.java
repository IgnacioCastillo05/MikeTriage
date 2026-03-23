package com.ecibet.mike.model.dto.sportdb;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;

import java.util.List;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class LeagueTableResponse {
    private List<LeagueTableEntry> table;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class LeagueTableEntry {
        private String idStanding;
        private int intRank;
        private String idTeam;
        private String strTeam;
        private String strBadge;
        private String idLeague;
        private String strLeague;
        private String strSeason;
        private String strForm;
        private String strDescription;
        private int intPlayed;
        private int intWin;
        private int intLoss;
        private int intDraw;
        private int intGoalsFor;
        private int intGoalsAgainst;
        private int intGoalDifference;
        private int intPoints;
        private String dateUpdated;
    }
}