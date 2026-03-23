package com.ecibet.mike.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OddsUpdateEventDTO {

    private String eventId;
    private String externalId;
    private Instant calculatedAt;
    private List<MarketOddsDTO> markets;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MarketOddsDTO {
        private String marketId;
        private String marketName;
        private String marketType;
        private List<SelectionOddsDTO> selections;
        private String reason;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SelectionOddsDTO {
        private String selectionId;
        private String selectionName;
        private Double newOdds;
        private Double probability;
        private Double adjustmentFactor;
    }
}