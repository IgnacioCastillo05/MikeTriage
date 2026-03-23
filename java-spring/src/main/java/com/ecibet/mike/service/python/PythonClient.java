package com.ecibet.mike.service.python;

import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class PythonClient {

    private final WebClient pythonWebClient;

    @Value("${ecibet.mike.python-service.timeout:5000}")
    private int timeout;

    public OddsUpdateEventDTO predictPreMatch(Map<String, Object> request) {
        try {
            return pythonWebClient.post()
                    .uri("/api/v1/predict/prematch")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(OddsUpdateEventDTO.class)
                    .timeout(Duration.ofMillis(timeout))
                    .block();
        } catch (Exception e) {
            log.error("Error calling Python service for pre-match: {}", e.getMessage());
            throw new RuntimeException("Python service unavailable", e);
        }
    }

    public OddsUpdateEventDTO predictLive(Map<String, Object> request) {
        try {
            return pythonWebClient.post()
                    .uri("/api/v1/predict/live")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(OddsUpdateEventDTO.class)
                    .timeout(Duration.ofMillis(timeout))
                    .block();
        } catch (Exception e) {
            log.error("Error calling Python service for live: {}", e.getMessage());
            throw new RuntimeException("Python service unavailable", e);
        }
    }

    public Object trainModel(Map<String, Object> request) {
        try {
            return pythonWebClient.post()
                    .uri("/api/v1/train/rf")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Object.class)
                    .timeout(Duration.ofMillis(timeout * 10))
                    .block();
        } catch (Exception e) {
            log.error("Error calling Python service for training: {}", e.getMessage());
            throw new RuntimeException("Python training service unavailable", e);
        }
    }
}