package com.ecibet.mike.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    @Value("${ecibet.mike.rabbitmq.exchanges.match-events}")
    private String matchEventsExchange;

    @Value("${ecibet.mike.rabbitmq.exchanges.odds-updated}")
    private String oddsUpdatedExchange;

    @Value("${ecibet.mike.rabbitmq.queues.mike-match-queue}")
    private String mikeMatchQueue;

    @Value("${ecibet.mike.rabbitmq.routing-keys.match-all}")
    private String matchAllRoutingKey;

    @Bean
    public TopicExchange matchEventsExchange() {
        return new TopicExchange(matchEventsExchange);
    }

    @Bean
    public TopicExchange oddsUpdatedExchange() {
        return new TopicExchange(oddsUpdatedExchange);
    }

    @Bean
    public Queue mikeMatchQueue() {
        return new Queue(mikeMatchQueue, true);
    }

    @Bean
    public Binding mikeMatchBinding() {
        return BindingBuilder
                .bind(mikeMatchQueue())
                .to(matchEventsExchange())
                .with(matchAllRoutingKey);
    }

    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        ObjectMapper objectMapper = new ObjectMapper();
        objectMapper.registerModule(new JavaTimeModule());
        objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        return new Jackson2JsonMessageConverter(objectMapper);
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        rabbitTemplate.setMessageConverter(messageConverter());
        return rabbitTemplate;
    }
}