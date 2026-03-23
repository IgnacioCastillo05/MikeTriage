package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.HistoricalMatch;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface HistoricalMatchRepository extends MongoRepository<HistoricalMatch, String> {

    Optional<HistoricalMatch> findByExternalId(String externalId);

    boolean existsByExternalId(String externalId);

    List<HistoricalMatch> findByMatchDateAfter(LocalDate date);

    List<HistoricalMatch> findByMatchDateBetween(LocalDate start, LocalDate end);

    List<HistoricalMatch> findByHomeTeamAndAwayTeam(String homeTeam, String awayTeam);
}