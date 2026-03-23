package com.ecibet.mike.controller;

import com.ecibet.mike.service.historical.HistoricalSyncService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/v1/historical")
@RequiredArgsConstructor
@Tag(name = "Sincronización Histórica", description = "Endpoints para sincronizar datos con SportDB")
public class HistoricalSyncController {

    private final HistoricalSyncService historicalSyncService;

    @PostMapping("/sync/full")
    @Operation(summary = "Sincronización completa de datos históricos")
    public ResponseEntity<Map<String, Object>> syncFull(@RequestParam(defaultValue = "5") int yearsBack) {
        log.info("Iniciando sincronización completa de {} años", yearsBack);
        Map<String, Object> result = historicalSyncService.syncHistoricalData(yearsBack);
        return ResponseEntity.accepted().body(result);
    }

    @PostMapping("/sync/incremental")
    @Operation(summary = "Sincronización incremental")
    public ResponseEntity<Map<String, Object>> syncIncremental() {
        log.info("Iniciando sincronización incremental");
        Map<String, Object> result = historicalSyncService.syncIncremental();
        return ResponseEntity.accepted().body(result);
    }

    @GetMapping("/status")
    @Operation(summary = "Estado de la sincronización")
    public ResponseEntity<Map<String, Object>> getSyncStatus() {
        return ResponseEntity.ok(historicalSyncService.getSyncStatus());
    }
}