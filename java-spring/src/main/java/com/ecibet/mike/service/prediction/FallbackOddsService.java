package com.ecibet.mike.service.prediction;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;

@Slf4j
@Service
public class FallbackOddsService {

    public OddsUpdateEventDTO getFallbackOdds(MatchEventDTO event) {
        log.warn("Usando fallback odds para evento: {}", event.getEventId());

        return OddsUpdateEventDTO.builder()
                .eventId(event.getEventId())
                .externalId(event.getExternalId())
                .calculatedAt(Instant.now())
                .markets(List.of(
                        OddsUpdateEventDTO.MarketOddsDTO.builder()
                                .marketId("1X2")
                                .marketName("Resultado Final")
                                .marketType("WIN_DRAW_WIN")
                                .selections(List.of(
                                        createSelection("HOME", event.getHomeTeam(), 2.10, 0.44),
                                        createSelection("DRAW", "Empate", 3.40, 0.28),
                                        createSelection("AWAY", event.getAwayTeam(), 3.80, 0.24)
                                ))
                                .reason("Odds por defecto - servicio no disponible")
                                .build()
                ))
                .build();
    }

    private OddsUpdateEventDTO.SelectionOddsDTO createSelection(String id, String name, double odds, double prob) {
        return OddsUpdateEventDTO.SelectionOddsDTO.builder()
                .selectionId(id)
                .selectionName(name)
                .newOdds(odds)
                .probability(prob)
                .adjustmentFactor(1.0)
                .build();
    }
}