package com.ecibet.mike.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class RestClientConfig {

    @Bean
    public WebClient pythonWebClient(
            @Value("${ecibet.mike.python-service.url}") String pythonServiceUrl) {
        return WebClient.builder()
                .baseUrl(pythonServiceUrl)
                .build();
    }

    @Bean
    public WebClient sportdbWebClient() {
        return WebClient.builder()
                .build();
    }
}