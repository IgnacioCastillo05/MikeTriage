package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.Team;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface TeamRepository extends MongoRepository<Team, String> {

    Optional<Team> findByExternalId(String externalId);

    boolean existsByExternalId(String externalId);

    Optional<Team> findByName(String name);

    List<Team> findByLeagueId(String leagueId);
}