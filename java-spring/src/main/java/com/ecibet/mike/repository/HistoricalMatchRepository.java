package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.HistoricalMatch;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface HistoricalMatchRepository extends MongoRepository<HistoricalMatch, String> {

    Optional<HistoricalMatch> findByExternalId(String externalId);

    boolean existsByExternalId(String externalId);

    List<HistoricalMatch> findByCompetition(String competition);

    List<HistoricalMatch> findByCompetitionAndSeason(String competition, String season);

    List<HistoricalMatch> findByHomeTeam(String teamName);

    List<HistoricalMatch> findByAwayTeam(String teamName);

    long countBySyncVersion(String syncVersion);
}