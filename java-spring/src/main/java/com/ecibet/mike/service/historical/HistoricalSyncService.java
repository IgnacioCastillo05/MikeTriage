package com.ecibet.mike.service.historical;

import com.ecibet.mike.model.dto.sportdb.LeagueTableResponse;
import com.ecibet.mike.model.dto.sportdb.SeasonEventsResponse;
import com.ecibet.mike.model.dto.sportdb.TeamResponse;
import com.ecibet.mike.model.dto.sportdb.AllLeaguesResponse;
import com.ecibet.mike.model.mongodb.HistoricalMatch;
import com.ecibet.mike.model.mongodb.Team;
import com.ecibet.mike.model.mongodb.League;
import com.ecibet.mike.model.mongodb.Standing;
import com.ecibet.mike.repository.HistoricalMatchRepository;
import com.ecibet.mike.repository.TeamRepository;
import com.ecibet.mike.repository.LeagueRepository;
import com.ecibet.mike.repository.StandingRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class HistoricalSyncService {

    private final SportDBClient sportDBClient;
    private final DataProcessor dataProcessor;
    private final HistoricalMatchRepository historicalMatchRepository;
    private final TeamRepository teamRepository;
    private final LeagueRepository leagueRepository;
    private final StandingRepository standingRepository;

    private static final List<String> MAIN_LEAGUES = List.of(
            "4328", "4335", "4332", "4331", "4334"
    );

    private static final List<String> SEASONS = List.of(
            "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"
    );

    public Map<String, Object> syncAllData() {
        log.info("Iniciando sincronizacion completa de datos");

        Map<String, Object> result = new HashMap<>();
        result.put("status", "started");
        result.put("startTime", LocalDateTime.now());

        int leaguesCount = 0;
        int teamsCount = 0;
        int standingsCount = 0;
        int matchesCount = 0;
        int errorCount = 0;

        try {
            AllLeaguesResponse allLeagues = sportDBClient.getAllLeagues().block();
            if (allLeagues != null && allLeagues.getLeagues() != null) {
                for (AllLeaguesResponse.LeagueEntry entry : allLeagues.getLeagues()) {
                    League league = dataProcessor.processLeague(entry);
                    if (!leagueRepository.existsByExternalId(league.getExternalId())) {
                        leagueRepository.save(league);
                        leaguesCount++;
                    }
                }
                log.info("Ligas sincronizadas: {}", leaguesCount);
            }

            for (String leagueId : MAIN_LEAGUES) {
                try {
                    TeamResponse teamResponse = sportDBClient.getTeamsByLeague(leagueId).block();
                    if (teamResponse != null && teamResponse.getTeams() != null) {
                        for (TeamResponse.TeamEntry entry : teamResponse.getTeams()) {
                            Team team = dataProcessor.processTeam(entry);
                            if (!teamRepository.existsByExternalId(team.getExternalId())) {
                                teamRepository.save(team);
                                teamsCount++;
                            }
                        }
                    }
                } catch (Exception e) {
                    log.error("Error sincronizando equipos liga {}: {}", leagueId, e.getMessage());
                    errorCount++;
                }
            }
            log.info("Equipos sincronizados: {}", teamsCount);

            for (String leagueId : MAIN_LEAGUES) {
                for (String season : SEASONS) {
                    try {
                        LeagueTableResponse standingResponse = sportDBClient.getLeagueTable(leagueId, season).block();

                        if (standingResponse != null && standingResponse.getTable() != null) {
                            for (LeagueTableResponse.LeagueTableEntry entry : standingResponse.getTable()) {
                                Standing standing = dataProcessor.processStanding(entry, leagueId, season);
                                if (!standingRepository.existsByExternalId(standing.getExternalId())) {
                                    standingRepository.save(standing);
                                    standingsCount++;
                                }
                            }
                            log.info("Tabla posiciones liga {} temporada {}: {} equipos", leagueId, season, standingResponse.getTable().size());
                        }

                        SeasonEventsResponse eventsResponse = sportDBClient.getSeasonEvents(leagueId, season).block();

                        if (eventsResponse != null && eventsResponse.getEvents() != null) {
                            for (SeasonEventsResponse.EventEntry event : eventsResponse.getEvents()) {
                                HistoricalMatch match = dataProcessor.processMatchEvent(event, leagueId, season);
                                match.setSyncVersion("sportdb_v1");
                                match.setSyncStatus("COMPLETED");
                                if (!historicalMatchRepository.existsByExternalId(match.getExternalId())) {
                                    historicalMatchRepository.save(match);
                                    matchesCount++;
                                }
                            }
                            log.info("Partidos liga {} temporada {}: {} partidos", leagueId, season, eventsResponse.getEvents().size());
                        }

                    } catch (Exception e) {
                        log.error("Error sincronizando liga {} temporada {}: {}", leagueId, season, e.getMessage());
                        errorCount++;
                    }
                }
            }

            result.put("leaguesCount", leaguesCount);
            result.put("teamsCount", teamsCount);
            result.put("standingsCount", standingsCount);
            result.put("matchesCount", matchesCount);
            result.put("errorCount", errorCount);
            result.put("status", "completed");
            result.put("endTime", LocalDateTime.now());
            log.info("Sincronizacion completada. Ligas: {}, Equipos: {}, Tablas: {}, Partidos: {}, Errores: {}",
                    leaguesCount, teamsCount, standingsCount, matchesCount, errorCount);

        } catch (Exception e) {
            log.error("Error en sincronizacion completa", e);
            result.put("status", "failed");
            result.put("error", e.getMessage());
        }

        return result;
    }

    public Map<String, Object> syncIncremental() {
        log.info("Iniciando sincronizacion incremental");

        Map<String, Object> result = new HashMap<>();
        result.put("status", "started");
        result.put("startTime", LocalDateTime.now());

        int leaguesCount = 0;
        int teamsCount = 0;
        int standingsCount = 0;
        int matchesCount = 0;
        int errorCount = 0;

        try {
            String currentSeason = "2024-2025";

            AllLeaguesResponse allLeagues = sportDBClient.getAllLeagues().block();
            if (allLeagues != null && allLeagues.getLeagues() != null) {
                for (AllLeaguesResponse.LeagueEntry entry : allLeagues.getLeagues()) {
                    League league = dataProcessor.processLeague(entry);
                    if (!leagueRepository.existsByExternalId(league.getExternalId())) {
                        leagueRepository.save(league);
                        leaguesCount++;
                    }
                }
            }

            for (String leagueId : MAIN_LEAGUES) {
                try {
                    TeamResponse teamResponse = sportDBClient.getTeamsByLeague(leagueId).block();
                    if (teamResponse != null && teamResponse.getTeams() != null) {
                        for (TeamResponse.TeamEntry entry : teamResponse.getTeams()) {
                            Team team = dataProcessor.processTeam(entry);
                            if (!teamRepository.existsByExternalId(team.getExternalId())) {
                                teamRepository.save(team);
                                teamsCount++;
                            }
                        }
                    }

                    LeagueTableResponse standingResponse = sportDBClient.getCurrentLeagueTable(leagueId).block();
                    if (standingResponse != null && standingResponse.getTable() != null) {
                        for (LeagueTableResponse.LeagueTableEntry entry : standingResponse.getTable()) {
                            Standing standing = dataProcessor.processStanding(entry, leagueId, currentSeason);
                            if (!standingRepository.existsByExternalId(standing.getExternalId())) {
                                standingRepository.save(standing);
                                standingsCount++;
                            }
                        }
                    }

                    SeasonEventsResponse eventsResponse = sportDBClient.getSeasonEvents(leagueId, currentSeason).block();
                    if (eventsResponse != null && eventsResponse.getEvents() != null) {
                        for (SeasonEventsResponse.EventEntry event : eventsResponse.getEvents()) {
                            HistoricalMatch match = dataProcessor.processMatchEvent(event, leagueId, currentSeason);
                            match.setSyncVersion("sportdb_v1");
                            match.setSyncStatus("COMPLETED");
                            if (!historicalMatchRepository.existsByExternalId(match.getExternalId())) {
                                historicalMatchRepository.save(match);
                                matchesCount++;
                            }
                        }
                    }

                } catch (Exception e) {
                    log.error("Error en sincronizacion incremental liga {}: {}", leagueId, e.getMessage());
                    errorCount++;
                }
            }

            result.put("leaguesCount", leaguesCount);
            result.put("teamsCount", teamsCount);
            result.put("standingsCount", standingsCount);
            result.put("matchesCount", matchesCount);
            result.put("errorCount", errorCount);
            result.put("status", "completed");
            result.put("endTime", LocalDateTime.now());
            log.info("Sincronizacion incremental completada. Ligas: {}, Equipos: {}, Tablas: {}, Partidos: {}, Errores: {}",
                    leaguesCount, teamsCount, standingsCount, matchesCount, errorCount);

        } catch (Exception e) {
            log.error("Error en sincronizacion incremental", e);
            result.put("status", "failed");
            result.put("error", e.getMessage());
        }

        return result;
    }

    public Map<String, Object> getSyncStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("leagues", leagueRepository.count());
        status.put("teams", teamRepository.count());
        status.put("standings", standingRepository.count());
        status.put("matches", historicalMatchRepository.count());
        status.put("status", "idle");
        return status;
    }

    public Map<String, Object> syncHistoricalData(int yearsBack) {
        log.info("Iniciando sincronizacion historica de {} años", yearsBack);

        Map<String, Object> result = new HashMap<>();
        result.put("status", "started");
        result.put("yearsBack", yearsBack);
        result.put("startTime", LocalDateTime.now());

        int leaguesCount = 0;
        int teamsCount = 0;
        int standingsCount = 0;
        int matchesCount = 0;
        int errorCount = 0;

        try {
            int seasonsToSync = Math.min(yearsBack, SEASONS.size());
            List<String> seasonsToSyncList = SEASONS.subList(SEASONS.size() - seasonsToSync, SEASONS.size());

            AllLeaguesResponse allLeagues = sportDBClient.getAllLeagues().block();
            if (allLeagues != null && allLeagues.getLeagues() != null) {
                for (AllLeaguesResponse.LeagueEntry entry : allLeagues.getLeagues()) {
                    League league = dataProcessor.processLeague(entry);
                    if (!leagueRepository.existsByExternalId(league.getExternalId())) {
                        leagueRepository.save(league);
                        leaguesCount++;
                    }
                }
                log.info("Ligas sincronizadas: {}", leaguesCount);
            }

            for (String leagueId : MAIN_LEAGUES) {
                try {
                    TeamResponse teamResponse = sportDBClient.getTeamsByLeague(leagueId).block();
                    if (teamResponse != null && teamResponse.getTeams() != null) {
                        for (TeamResponse.TeamEntry entry : teamResponse.getTeams()) {
                            Team team = dataProcessor.processTeam(entry);
                            if (!teamRepository.existsByExternalId(team.getExternalId())) {
                                teamRepository.save(team);
                                teamsCount++;
                            }
                        }
                    }
                } catch (Exception e) {
                    log.error("Error sincronizando equipos liga {}: {}", leagueId, e.getMessage());
                    errorCount++;
                }
            }
            log.info("Equipos sincronizados: {}", teamsCount);

            for (String leagueId : MAIN_LEAGUES) {
                for (String season : seasonsToSyncList) {
                    try {
                        LeagueTableResponse standingResponse = sportDBClient.getLeagueTable(leagueId, season).block();
                        if (standingResponse != null && standingResponse.getTable() != null) {
                            for (LeagueTableResponse.LeagueTableEntry entry : standingResponse.getTable()) {
                                Standing standing = dataProcessor.processStanding(entry, leagueId, season);
                                if (!standingRepository.existsByExternalId(standing.getExternalId())) {
                                    standingRepository.save(standing);
                                    standingsCount++;
                                }
                            }
                            log.info("Tabla posiciones liga {} temporada {}: {} equipos", leagueId, season, standingResponse.getTable().size());
                        }

                        SeasonEventsResponse eventsResponse = sportDBClient.getSeasonEvents(leagueId, season).block();
                        if (eventsResponse != null && eventsResponse.getEvents() != null) {
                            for (SeasonEventsResponse.EventEntry event : eventsResponse.getEvents()) {
                                HistoricalMatch match = dataProcessor.processMatchEvent(event, leagueId, season);
                                match.setSyncVersion("sportdb_v1");
                                match.setSyncStatus("COMPLETED");
                                if (!historicalMatchRepository.existsByExternalId(match.getExternalId())) {
                                    historicalMatchRepository.save(match);
                                    matchesCount++;
                                }
                            }
                            log.info("Partidos liga {} temporada {}: {} partidos", leagueId, season, eventsResponse.getEvents().size());
                        }

                    } catch (Exception e) {
                        log.error("Error sincronizando liga {} temporada {}: {}", leagueId, season, e.getMessage());
                        errorCount++;
                    }
                }
            }

            result.put("leaguesCount", leaguesCount);
            result.put("teamsCount", teamsCount);
            result.put("standingsCount", standingsCount);
            result.put("matchesCount", matchesCount);
            result.put("errorCount", errorCount);
            result.put("status", "completed");
            result.put("endTime", LocalDateTime.now());
            log.info("Sincronizacion historica completada. Ligas: {}, Equipos: {}, Tablas: {}, Partidos: {}, Errores: {}",
                    leaguesCount, teamsCount, standingsCount, matchesCount, errorCount);

        } catch (Exception e) {
            log.error("Error en sincronizacion historica", e);
            result.put("status", "failed");
            result.put("error", e.getMessage());
        }

        return result;
    }
}