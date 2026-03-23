package com.ecibet.mike.scheduler;

import com.ecibet.mike.service.historical.HistoricalSyncService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class HistoricalSyncScheduler {

    private final HistoricalSyncService historicalSyncService;

    @Scheduled(cron = "0 0 3 * * ?")
    public void syncIncrementalDaily() {
        log.info("Ejecutando sincronización incremental programada");
        try {
            historicalSyncService.syncIncremental();
            log.info("Sincronización incremental completada");
        } catch (Exception e) {
            log.error("Error en sincronización incremental programada: {}", e.getMessage(), e);
        }
    }

    @Scheduled(cron = "0 0 4 * * 1")
    public void syncFullWeekly() {
        log.info("Ejecutando sincronización completa semanal");
        try {
            historicalSyncService.syncHistoricalData(1);
            log.info("Sincronización completa semanal completada");
        } catch (Exception e) {
            log.error("Error en sincronización completa semanal: {}", e.getMessage(), e);
        }
    }
}