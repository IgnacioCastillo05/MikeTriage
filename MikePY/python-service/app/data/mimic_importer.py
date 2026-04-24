
import logging
import pandas as pd
from typing import List, Dict, Any
from google.cloud import bigquery
from ..config.triage_settings import settings

logger = logging.getLogger(__name__)

class MIMICImporter:
    def __init__(self):
        self.client = None
        self.project_id = settings.MIMIC_PROJECT_ID
        
    def setup_bigquery_client(self):
        if self.project_id:
            self.client = bigquery.Client(project=self.project_id)
            logger.info("Cliente BigQuery inicializado")
            return True
        else:
            logger.warning("MIMIC_PROJECT_ID no configurado")
            return False
    
    def load_ed_stays(self, limit: int = 1000) -> List[Dict[str, Any]]:
        if not self.setup_bigquery_client():
            return []
            
        query = f"""
        SELECT 
            ed.subject_id,
            ed.hadm_id,
            ed.intime,
            ed.outtime,
            ed.disposition,
            diag.icd_code,
            diag.icd_version
        FROM `{settings.MIMIC_DATASET_ID}.ed.edstays` ed
        LEFT JOIN `{settings.MIMIC_DATASET_ID}.ed.diagnosis` diag
            ON ed.subject_id = diag.subject_id AND ed.hadm_id = diag.hadm_id
        LIMIT {limit}
        """
        
        try:
            df = self.client.query(query).to_dataframe()
            logger.info(f"Cargadas {len(df)} estancias de emergencia")
            
            cases = []
            for _, row in df.iterrows():
                case = {
                    "subject_id": row.get("subject_id"),
                    "sintomas": [str(row.get("icd_code", "dolor"))],
                    "vital_signs": self._get_vital_signs(row.get("subject_id")),
                    "nivelPrioridad": self._map_disposition_to_triage(row.get("disposition")),
                    "antecedentes": [],
                    "comentario": f"ICD: {row.get('icd_code')}"
                }
                cases.append(case)
                
            return cases
            
        except Exception as e:
            logger.error(f"Error cargando MIMIC: {e}")
            return []
    
    def _get_vital_signs(self, subject_id: int) -> Dict[str, float]:
        query = f"""
        SELECT 
            charttime,
            valuenum,
            itemid
        FROM `{settings.MIMIC_DATASET_ID}.icu.chartevents`
        WHERE subject_id = {subject_id}
            AND itemid IN (220045, 223761, 220210, 220179, 220180, 220277)
        ORDER BY charttime DESC
        LIMIT 1
        """
        
        try:
            df = self.client.query(query).to_dataframe()
            if not df.empty:
                return {
                    "temperature_c": float(df[df["itemid"] == 223761]["valuenum"].iloc[0]) if 223761 in df["itemid"].values else 36.8,
                    "heart_rate_bpm": float(df[df["itemid"] == 220045]["valuenum"].iloc[0]) if 220045 in df["itemid"].values else 75,
                    "respiratory_rate_bpm": float(df[df["itemid"] == 220210]["valuenum"].iloc[0]) if 220210 in df["itemid"].values else 16,
                    "systolic_bp_mmhg": float(df[df["itemid"] == 220179]["valuenum"].iloc[0]) if 220179 in df["itemid"].values else 118,
                    "diastolic_bp_mmhg": float(df[df["itemid"] == 220180]["valuenum"].iloc[0]) if 220180 in df["itemid"].values else 76,
                    "oxygen_saturation_pct": float(df[df["itemid"] == 220277]["valuenum"].iloc[0]) if 220277 in df["itemid"].values else 98,
                    "weight_kg": 70,
                    "height_cm": 170
                }
        except Exception:
            pass
            
        return {
            "temperature_c": 36.8,
            "heart_rate_bpm": 75,
            "respiratory_rate_bpm": 16,
            "systolic_bp_mmhg": 118,
            "diastolic_bp_mmhg": 76,
            "oxygen_saturation_pct": 98,
            "weight_kg": 70,
            "height_cm": 170
        }
    
    def _map_disposition_to_triage(self, disposition: str) -> int:
        mapping = {
            "HOME": 4,
            "ICU": 1,
            "WARD": 3,
            "OBSERVATION": 3,
            "DECEASED": 1,
            "TRANSFER": 2
        }
        return mapping.get(str(disposition).upper(), 3)

mimic_importer = MIMICImporter()