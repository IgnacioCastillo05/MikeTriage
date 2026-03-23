package com.ecibet.mike.model.mongodb;

import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "prediction_audit")
public class PredictionAudit {

    @Id
    private String id;

    @Indexed
    private String eventId;

    private String eventType;
    private Integer minute;
    private Integer homeScore;
    private Integer awayScore;

    private OddsUpdateEventDTO predictedOdds;

    private Map<String, Object> featuresUsed;
    private Map<String, Double> featureImportance;
    private Boolean gptFeaturesUsed;

    private String predictionSource;
    private Long responseTimeMs;

    private Instant createdAt;
}