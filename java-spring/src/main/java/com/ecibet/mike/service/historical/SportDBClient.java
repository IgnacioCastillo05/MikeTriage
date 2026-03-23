package com.ecibet.mike.service.historical;

import com.ecibet.mike.config.SportDBConfig;
import com.ecibet.mike.model.dto.sportdb.AllLeaguesResponse;
import com.ecibet.mike.model.dto.sportdb.LeagueTableResponse;
import com.ecibet.mike.model.dto.sportdb.SeasonEventsResponse;
import com.ecibet.mike.model.dto.sportdb.TeamResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Slf4j
@Service
@RequiredArgsConstructor
public class SportDBClient {

    private final WebClient sportdbWebClient;
    private final SportDBConfig sportDBConfig;

    public Mono<LeagueTableResponse> getLeagueTable(String leagueId, String season) {
        String url = sportDBConfig.buildUrl("lookuptable.php");
        String fullUrl = url + "?l=" + leagueId + "&s=" + season;
        log.info("Llamando a SportDB: {}", fullUrl);

        return sportdbWebClient.get()
                .uri(fullUrl)
                .retrieve()
                .bodyToMono(LeagueTableResponse.class)
                .doOnSuccess(response -> log.info("Obtenidos {} equipos para liga {} temporada {}",
                        response.getTable() != null ? response.getTable().size() : 0,
                        leagueId, season))
                .doOnError(error -> log.error("Error fetching league table: {}", error.getMessage()));
    }

    public Mono<LeagueTableResponse> getCurrentLeagueTable(String leagueId) {
        String url = sportDBConfig.buildUrl("lookuptable.php");
        String fullUrl = url + "?l=" + leagueId;
        log.info("Llamando a SportDB: {}", fullUrl);

        return sportdbWebClient.get()
                .uri(fullUrl)
                .retrieve()
                .bodyToMono(LeagueTableResponse.class)
                .doOnSuccess(response -> log.info("Obtenidos {} equipos para liga {}",
                        response.getTable() != null ? response.getTable().size() : 0,
                        leagueId))
                .doOnError(error -> log.error("Error fetching current league table: {}", error.getMessage()));
    }

    public Mono<SeasonEventsResponse> getSeasonEvents(String leagueId, String season) {
        String url = sportDBConfig.buildUrl("eventsseason.php");
        String fullUrl = url + "?id=" + leagueId + "&s=" + season;
        log.info("Llamando a SportDB: {}", fullUrl);

        return sportdbWebClient.get()
                .uri(fullUrl)
                .retrieve()
                .bodyToMono(SeasonEventsResponse.class)
                .doOnSuccess(response -> log.info("Obtenidos {} partidos para liga {} temporada {}",
                        response.getEvents() != null ? response.getEvents().size() : 0,
                        leagueId, season))
                .doOnError(error -> log.error("Error fetching season events: {}", error.getMessage()));
    }


    public Mono<AllLeaguesResponse> getAllLeagues() {
        String url = sportDBConfig.buildUrl("all_leagues.php");
        log.info("Llamando a SportDB: {}", url);

        return sportdbWebClient.get()
                .uri(url)
                .retrieve()
                .bodyToMono(AllLeaguesResponse.class)
                .doOnSuccess(response -> log.info("Obtenidas {} ligas",
                        response.getLeagues() != null ? response.getLeagues().size() : 0))
                .doOnError(error -> log.error("Error fetching all leagues: {}", error.getMessage()));
    }

    public Mono<TeamResponse> getTeamsByLeague(String leagueId) {
        String url = sportDBConfig.buildUrl("search_all_teams.php");
        String fullUrl = url + "?l=" + leagueId;
        log.info("Llamando a SportDB: {}", fullUrl);

        return sportdbWebClient.get()
                .uri(fullUrl)
                .retrieve()
                .bodyToMono(TeamResponse.class)
                .doOnSuccess(response -> log.info("Obtenidos {} equipos para liga {}",
                        response.getTeams() != null ? response.getTeams().size() : 0, leagueId))
                .doOnError(error -> log.error("Error fetching teams by league: {}", error.getMessage()));
    }
}