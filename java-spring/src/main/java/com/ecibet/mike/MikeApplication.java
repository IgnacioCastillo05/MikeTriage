package com.ecibet.mike;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Map;

@SpringBootApplication
@RestController
public class MikeApplication {

    public static void main(String[] args) {
        SpringApplication.run(MikeApplication.class, args);
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "healthy", "service", "mike-java");
    }

    @GetMapping("/")
    public Map<String, String> root() {
        return Map.of("service", "Mike Java Service", "version", "1.0.0");
    }
}