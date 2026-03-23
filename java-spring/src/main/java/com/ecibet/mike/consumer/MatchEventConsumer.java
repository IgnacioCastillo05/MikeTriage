package com.ecibet.mike.consumer;

import com.ecibet.mike.model.dto.MatchEventDTO;
import com.ecibet.mike.service.prediction.OddsPredictionService;
import com.ecibet.mike.utils.MinuteChecker;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class MatchEventConsumer {

    private final OddsPredictionService oddsPredictionService;
    private final MinuteChecker minuteChecker;

    @RabbitListener(queues = "${ecibet.mike.rabbitmq.queues.mike-match-queue}")
    public void consumeMatchEvent(MatchEventDTO event) {
        log.info("Mike recibió evento: {} para partido: {} minuto: {}",
                event.getEventType(), event.getEventId(), event.getMinute());

        try {
            boolean needGPTFeatures = minuteChecker.shouldGenerateGPTFeatures(
                    event.getMinute(),
                    event.getEventType()
            );

            oddsPredictionService.processEvent(event, needGPTFeatures);

        } catch (Exception e) {
            log.error("Error procesando evento: {}", e.getMessage(), e);
        }
    }
}