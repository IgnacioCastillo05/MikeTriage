package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.Standing;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface StandingRepository extends MongoRepository<Standing, String> {

    Optional<Standing> findByExternalId(String externalId);

    boolean existsByExternalId(String externalId);

    List<Standing> findByLeagueIdAndSeason(String leagueId, String season);

    List<Standing> findByTeamId(String teamId);

    Optional<Standing> findByTeamNameAndLeagueIdAndSeason(String teamName, String leagueId, String season);
}