package com.ecibet.mike.service.historical;

import com.ecibet.mike.model.mongodb.HistoricalMatch;
import com.ecibet.mike.repository.HistoricalMatchRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileWriter;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class TrainingDataExporter {

    private final HistoricalMatchRepository repository;
    private final FeatureCalculator featureCalculator;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public void exportForRandomForest(String outputPath) {
        log.info("Exportando datos para entrenamiento de Random Forest");

        try {
            List<HistoricalMatch> matches = repository.findByMatchDateAfter(LocalDate.now().minusYears(3));

            File file = new File(outputPath, "rf_training_data.json");

            try (FileWriter writer = new FileWriter(file)) {
                for (HistoricalMatch match : matches) {
                    Map<String, Double> features = featureCalculator.extractFeatures(match);
                    String json = objectMapper.writeValueAsString(features);
                    writer.write(json + "\n");
                }
            }

            log.info("Exportados {} partidos para entrenamiento", matches.size());

        } catch (Exception e) {
            log.error("Error exportando datos: {}", e.getMessage());
        }
    }

    public void exportForGPTFineTuning(String outputPath) {
        log.info("Exportando datos para fine-tuning de GPT");

        try {
            List<HistoricalMatch> matches = repository.findByMatchDateAfter(LocalDate.now().minusYears(2));

            File file = new File(outputPath, "gpt_finetuning.jsonl");

            try (FileWriter writer = new FileWriter(file)) {
                for (HistoricalMatch match : matches) {
                    Map<String, Object> example = buildGPTExample(match);
                    String json = objectMapper.writeValueAsString(example);
                    writer.write(json + "\n");
                }
            }

            log.info("Exportados {} ejemplos para fine-tuning", matches.size());

        } catch (Exception e) {
            log.error("Error exportando para fine-tuning: {}", e.getMessage());
        }
    }

    private Map<String, Object> buildGPTExample(HistoricalMatch match) {
        return Map.of(
                "messages", List.of(
                        Map.of("role", "system", "content", "Eres MIKE, experto en predicción de odds deportivas."),
                        Map.of("role", "user", "content", buildUserPrompt(match)),
                        Map.of("role", "assistant", "content", buildAssistantResponse(match))
                )
        );
    }

    private String buildUserPrompt(HistoricalMatch match) {
        return String.format("PARTIDO: %s vs %s\nCOMPETICIÓN: %s\nGENERA ODDS PARA 1X2",
                match.getHomeTeam(), match.getAwayTeam(), match.getCompetition());
    }

    private String buildAssistantResponse(HistoricalMatch match) {
        return String.format("{\"home\": %.2f, \"draw\": %.2f, \"away\": %.2f}",
                2.10, 3.40, 3.80);
    }
}