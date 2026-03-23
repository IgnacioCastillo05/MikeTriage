package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.MatchContext;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

@Repository
public interface MatchContextRepository extends MongoRepository<MatchContext, String> {

    Optional<MatchContext> findByEventId(String eventId);

    List<MatchContext> findByStatus(String status);

    List<MatchContext> findByLastUpdateBefore(Instant instant);
}