package com.ecibet.mike.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenAIConfig {

    @Value("${ecibet.mike.openai.api-key:}")
    private String apiKey;

    @Value("${ecibet.mike.openai.model:gpt-4o}")
    private String model;

    public String getApiKey() {
        return apiKey;
    }

    public String getModel() {
        return model;
    }

    public boolean isConfigured() {
        return apiKey != null && !apiKey.isEmpty();
    }
}