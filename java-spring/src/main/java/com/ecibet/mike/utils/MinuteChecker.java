package com.ecibet.mike.utils;

import org.springframework.stereotype.Component;

import java.util.Set;

@Component
public class MinuteChecker {

    private static final Set<String> SIGNIFICANT_EVENTS = Set.of(
            "GOAL", "RED_CARD", "HALFTIME", "STATUS_CHANGE"
    );

    public boolean shouldGenerateGPTFeatures(int minute, String eventType) {
        if (isMinuteUpdateOnly(eventType)) {
            return false;
        }

        if (minute <= 10) {
            return true;
        }

        if (minute >= 40 && minute <= 45) {
            return true;
        }

        if (minute >= 45 && minute <= 50) {
            return true;
        }

        if (minute >= 80 && minute <= 90) {
            return true;
        }

        if (minute > 90) {
            return true;
        }

        if (isSignificantEvent(eventType)) {
            return true;
        }

        return false;
    }

    public boolean isMinuteUpdateOnly(String eventType) {
        return "MINUTE_UPDATE".equals(eventType);
    }

    private boolean isSignificantEvent(String eventType) {
        return SIGNIFICANT_EVENTS.contains(eventType);
    }
}