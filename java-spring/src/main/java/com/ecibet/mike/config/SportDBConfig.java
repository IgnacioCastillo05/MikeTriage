package com.ecibet.mike.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Configuration
public class SportDBConfig {

    @Value("${ecibet.mike.sportdb.api-key}")
    private String apiKey;

    @Value("${ecibet.mike.sportdb.base-url}")
    private String baseUrl;

    @PostConstruct
    public void init() {
        log.info("========== SPORTDB CONFIG ==========");
        log.info("API Key: {}", apiKey);
        log.info("Base URL: {}", baseUrl);
        log.info("===================================");
    }

    public String getApiKey() {
        return apiKey;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public String buildUrl(String endpoint) {

        String cleanBaseUrl = baseUrl.replaceAll("/json$", "").replaceAll("/$", "");
        String url = cleanBaseUrl + "/json/" + apiKey + "/" + endpoint;
        log.debug("Built URL: {}", url);
        return url;
    }
}