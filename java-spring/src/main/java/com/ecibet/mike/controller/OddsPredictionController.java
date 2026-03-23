package com.ecibet.mike.controller;

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

    @PostMapping("/force/{eventId}")
    @Operation(summary = "Forzar predicción para un partido")
    public ResponseEntity<OddsUpdateEventDTO> forcePrediction(
            @PathVariable String eventId,
            @RequestParam boolean useGptFeatures) {
        log.info("Forzando predicción para eventId: {}, useGptFeatures: {}", eventId, useGptFeatures);
        OddsUpdateEventDTO result = oddsPredictionService.forcePrediction(eventId, useGptFeatures);
        return ResponseEntity.ok(result);
    }

    @GetMapping("/health")
    @Operation(summary = "Verificar estado del servicio")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("OK");
    }
}