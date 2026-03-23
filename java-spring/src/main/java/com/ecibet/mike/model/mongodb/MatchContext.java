package com.ecibet.mike.model.mongodb;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "match_contexts")
public class MatchContext {

    @Id
    private String id;

    @Indexed(unique = true)
    private String eventId;

    private String externalId;

    private String homeTeam;
    private String awayTeam;
    private String competition;

    private Integer minute;
    private Integer homeScore;
    private Integer awayScore;
    private String status;

    private String homeForm;
    private String awayForm;
    private Integer homePosition;
    private Integer awayPosition;
    private String homeInjuries;
    private String awayInjuries;

    private Map<String, Object> preMatchFeatures;
    private Map<String, Double> gptFeatures;

    private List<MatchEventDTO> eventHistory;

    private OddsUpdateEventDTO lastOdds;

    private Instant createdAt;
    private Instant lastUpdate;

    public void addEvent(MatchEventDTO event) {
        if (eventHistory == null) {
            eventHistory = new ArrayList<>();
        }
        eventHistory.add(event);
    }

    public List<MatchEventDTO> getEventHistory() {
        if (eventHistory == null) {
            eventHistory = new ArrayList<>();
        }
        return eventHistory;
    }

    public void setEventHistory(List<MatchEventDTO> eventHistory) {
        this.eventHistory = eventHistory;
    }
}