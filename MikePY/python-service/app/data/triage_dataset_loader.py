
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datasets import load_dataset
import random

logger = logging.getLogger(__name__)

class TriageDatasetLoader:
    def __init__(self):
        self.dataset = None
        
    def load_fedmll_triage(self, split: str = "train") -> List[Dict[str, Any]]:
        try:
            logger.info("Cargando dataset FEDMLL ED Triage desde HuggingFace")
            self.dataset = load_dataset("olaflaitinen/fedmml-ed-triage", split=split)
            
            cases = []
            for item in self.dataset:
                case = {
                    "sintomas": self._extract_symptoms(item),
                    "vital_signs": self._extract_vital_signs(item),
                    "nivelPrioridad": self._map_triage_level(item.get("triage_level", 3)),
                    "embarazo": False,
                    "antecedentes": [],
                    "comentario": item.get("chief_complaint", "")
                }
                cases.append(case)
                
            logger.info(f"Cargados {len(cases)} casos de triaje")
            return cases
            
        except Exception as e:
            logger.error(f"Error cargando FEDMLL: {e}")
            return []
    
    def _extract_symptoms(self, item: Dict) -> List[str]:
        chief_complaint = item.get("chief_complaint", "")
        if chief_complaint:
            return [chief_complaint.lower()]
        return ["dolor"]
    
    def _extract_vital_signs(self, item: Dict) -> Dict[str, float]:
        return {
            "temperature_c": float(item.get("temperature", 36.5)),
            "heart_rate_bpm": float(item.get("heart_rate", 75)),
            "respiratory_rate_bpm": float(item.get("respiratory_rate", 16)),
            "systolic_bp_mmhg": float(item.get("systolic_bp", 110)),
            "diastolic_bp_mmhg": float(item.get("diastolic_bp", 70)),
            "oxygen_saturation_pct": float(item.get("oxygen_saturation", 98)),
            "weight_kg": 70.0,
            "height_cm": 170.0
        }
    
    def _map_triage_level(self, level) -> int:
        if isinstance(level, int):
            return min(max(level, 1), 5)
        return 3

triage_dataset_loader = TriageDatasetLoader()