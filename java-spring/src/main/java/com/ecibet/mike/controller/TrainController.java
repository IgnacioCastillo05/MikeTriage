package com.ecibet.mike.controller;

import com.ecibet.mike.service.python.PythonClient;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/v1/train")
@RequiredArgsConstructor
@Tag(name = "Entrenamiento", description = "Endpoints para entrenar modelos")
public class TrainController {

    private final PythonClient pythonClient;

    @PostMapping("/rf")
    @Operation(summary = "Entrenar Random Forest")
    public ResponseEntity<Map<String, Object>> trainRandomForest() {
        log.info("Iniciando entrenamiento de Random Forest");

        Map<String, Object> request = new HashMap<>();
        request.put("action", "train");
        request.put("model_type", "random_forest");

        try {
            Object response = pythonClient.trainModel(request);
            return ResponseEntity.ok((Map<String, Object>) response);
        } catch (Exception e) {
            log.error("Error entrenando Random Forest: {}", e.getMessage());
            Map<String, Object> error = new HashMap<>();
            error.put("status", "error");
            error.put("message", e.getMessage());
            return ResponseEntity.internalServerError().body(error);
        }
    }

    @GetMapping("/status")
    @Operation(summary = "Estado del entrenamiento")
    public ResponseEntity<Map<String, Object>> getTrainingStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("status", "idle");
        status.put("last_training", null);
        status.put("models_available", false);
        return ResponseEntity.ok(status);
    }
}