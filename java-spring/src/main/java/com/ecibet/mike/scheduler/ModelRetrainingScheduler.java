package com.ecibet.mike.scheduler;

import com.ecibet.mike.service.python.PythonClient;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class ModelRetrainingScheduler {

    private final PythonClient pythonClient;

    @Scheduled(cron = "0 0 5 * * 1")
    public void retrainRandomForest() {
        log.info("Iniciando reentrenamiento programado de Random Forest");
        try {
            Map<String, Object> request = new HashMap<>();
            request.put("action", "retrain");
            request.put("model_type", "random_forest");

            pythonClient.predictPreMatch(request);
            log.info("Reentrenamiento de Random Forest completado");
        } catch (Exception e) {
            log.error("Error en reentrenamiento de Random Forest: {}", e.getMessage(), e);
        }
    }

    @Scheduled(cron = "0 0 6 * * 1")
    public void prepareGPTFineTuning() {
        log.info("Preparando datos para fine-tuning de GPT");
        try {
            log.info("Preparación de datos para fine-tuning completada");
        } catch (Exception e) {
            log.error("Error preparando datos para fine-tuning: {}", e.getMessage(), e);
        }
    }
}