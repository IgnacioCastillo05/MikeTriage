package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.League;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface LeagueRepository extends MongoRepository<League, String> {

    Optional<League> findByExternalId(String externalId);

    boolean existsByExternalId(String externalId);

    Optional<League> findByName(String name);
}