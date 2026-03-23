package com.ecibet.mike.repository;

import com.ecibet.mike.model.mongodb.PredictionAudit;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.List;

@Repository
public interface PredictionAuditRepository extends MongoRepository<PredictionAudit, String> {

    List<PredictionAudit> findByEventId(String eventId);

    List<PredictionAudit> findByCreatedAtBetween(Instant start, Instant end);
}