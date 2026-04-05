package com.ecibet.mike.controller;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import com.ecibet.mike.service.prediction.OddsPredictionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/v1/predict")
@RequiredArgsConstructor
@Tag(name = "Predicciones", description = "Endpoints para predicción de odds")
public class OddsPredictionController {

    private final OddsPredictionService oddsPredictionService;

    @PostMapping("/force")
    @Operation(summary = "Forzar predicción para un partido")
    public ResponseEntity<OddsUpdateEventDTO> forcePrediction(
            @RequestBody MatchEventDTO event,
            @RequestParam boolean useGptFeatures) {
        log.info("Forzando predicción para: {} vs {}, useGptFeatures: {}",
                event.getHomeTeam(), event.getAwayTeam(), useGptFeatures);
        OddsUpdateEventDTO result = oddsPredictionService.forcePrediction(event, useGptFeatures);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/health")
    @Operation(summary = "Verificar estado del servicio")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("OK");
    }
}