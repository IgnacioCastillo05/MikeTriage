package com.ecibet.mike.service.publisher;

import com.ecibet.mike.model.dto.OddsUpdateEventDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class OddsPublisher {

    private final RabbitTemplate rabbitTemplate;

    @Value("${ecibet.mike.rabbitmq.exchanges.odds-updated}")
    private String oddsUpdatedExchange;

    @Value("${ecibet.mike.rabbitmq.routing-keys.odds-updated}")
    private String oddsUpdatedRoutingKey;

    public void publish(OddsUpdateEventDTO odds) {
        try {
            rabbitTemplate.convertAndSend(oddsUpdatedExchange, oddsUpdatedRoutingKey, odds);
            log.debug("Odds publicadas para evento: {}", odds.getEventId());
        } catch (Exception e) {
            log.error("Error publicando odds: {}", e.getMessage(), e);
            throw e;
        }
    }
}