package com.ecibet.mike.service.historical;

import com.ecibet.mike.model.dto.sportdb.LeagueTableResponse;
import com.ecibet.mike.model.dto.sportdb.SeasonEventsResponse;
import com.ecibet.mike.model.dto.sportdb.TeamResponse;
import com.ecibet.mike.model.dto.sportdb.AllLeaguesResponse;
import com.ecibet.mike.model.mongodb.HistoricalMatch;
import com.ecibet.mike.model.mongodb.Team;
import com.ecibet.mike.model.mongodb.League;
import com.ecibet.mike.model.mongodb.Standing;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Slf4j
@Component
public class DataProcessor {

    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    public League processLeague(AllLeaguesResponse.LeagueEntry entry) {
        League league = new League();
        league.setExternalId(entry.getIdLeague());
        league.setName(entry.getStrLeague());
        league.setAlternateName(entry.getStrLeagueAlternate());
        league.setSport(entry.getStrSport());
        league.setCountry(entry.getStrCountry());
        league.setWebsite(entry.getStrWebsite());
        league.setFacebook(entry.getStrFacebook());
        league.setInstagram(entry.getStrInstagram());
        league.setTwitter(entry.getStrTwitter());
        league.setYoutube(entry.getStrYoutube());
        league.setDescription(entry.getStrDescriptionEN());
        league.setLogo(entry.getStrLogo());
        league.setBadge(entry.getStrBadge());
        league.setTrophy(entry.getStrTrophy());
        return league;
    }

    public Team processTeam(TeamResponse.TeamEntry entry) {
        Team team = new Team();
        team.setExternalId(entry.getIdTeam());
        team.setName(entry.getStrTeam());
        team.setShortName(entry.getStrTeamShort());
        team.setAlternateName(entry.getStrAlternate());
        team.setLeagueId(entry.getIdLeague());
        team.setLeagueName(entry.getStrLeague());
        team.setStadium(entry.getStrStadium());
        team.setStadiumLocation(entry.getStrStadiumLocation());
        if (entry.getIntStadiumCapacity() != null && !entry.getIntStadiumCapacity().isEmpty()) {
            team.setStadiumCapacity(Integer.parseInt(entry.getIntStadiumCapacity()));
        }
        if (entry.getIntFormedYear() != null && !entry.getIntFormedYear().isEmpty()) {
            team.setFormedYear(Integer.parseInt(entry.getIntFormedYear()));
        }
        team.setCountry(entry.getStrCountry());
        team.setWebsite(entry.getStrWebsite());
        team.setFacebook(entry.getStrFacebook());
        team.setInstagram(entry.getStrInstagram());
        team.setTwitter(entry.getStrTwitter());
        team.setYoutube(entry.getStrYoutube());
        team.setDescription(entry.getStrDescriptionEN());
        team.setBadge(entry.getStrBadge());
        team.setJersey(entry.getStrJersey());
        team.setLogo(entry.getStrLogo());
        return team;
    }

    public Standing processStanding(LeagueTableResponse.LeagueTableEntry entry, String leagueId, String season) {
        Standing standing = new Standing();
        standing.setExternalId(entry.getIdStanding());
        standing.setTeamId(entry.getIdTeam());
        standing.setTeamName(entry.getStrTeam());
        standing.setTeamBadge(entry.getStrBadge());
        standing.setLeagueId(leagueId);
        standing.setLeagueName(entry.getStrLeague());
        standing.setSeason(season);
        standing.setRank(entry.getIntRank());
        standing.setForm(entry.getStrForm());
        standing.setDescription(entry.getStrDescription());
        standing.setPlayed(entry.getIntPlayed());
        standing.setWins(entry.getIntWin());
        standing.setDraws(entry.getIntDraw());
        standing.setLosses(entry.getIntLoss());
        standing.setGoalsFor(entry.getIntGoalsFor());
        standing.setGoalsAgainst(entry.getIntGoalsAgainst());
        standing.setGoalDifference(entry.getIntGoalDifference());
        standing.setPoints(entry.getIntPoints());
        return standing;
    }

    public HistoricalMatch processMatchEvent(SeasonEventsResponse.EventEntry event, String leagueId, String season) {
        HistoricalMatch match = new HistoricalMatch();
        match.setExternalId(event.getIdEvent());
        match.setHomeTeam(event.getStrHomeTeam());
        match.setAwayTeam(event.getStrAwayTeam());

        if (event.getIntHomeScore() != null && !event.getIntHomeScore().isEmpty()) {
            match.setHomeScore(Integer.parseInt(event.getIntHomeScore()));
        }
        if (event.getIntAwayScore() != null && !event.getIntAwayScore().isEmpty()) {
            match.setAwayScore(Integer.parseInt(event.getIntAwayScore()));
        }

        match.setCompetition(event.getStrLeague());
        match.setCompetitionId(leagueId);
        match.setSeason(season);

        if (event.getDateEvent() != null && !event.getDateEvent().isEmpty()) {
            try {
                LocalDate date = LocalDate.parse(event.getDateEvent(), DATE_FORMATTER);
                match.setMatchDate(date);
            } catch (Exception e) {
                log.warn("Error parsing date: {}", event.getDateEvent());
            }
        }

        match.setStatus(event.getStrStatus());
        match.setMatchType("MATCH");
        match.setSyncedAt(LocalDateTime.now());
        match.setSyncVersion("sportdb_v1");
        match.setSyncStatus("COMPLETED");
        match.setCreatedAt(LocalDateTime.now());
        match.setUpdatedAt(LocalDateTime.now());

        return match;
    }
}