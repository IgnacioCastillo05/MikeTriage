
import logging
import subprocess
import json
import os
import random
import pandas as pd
from typing import List, Dict, Any
from ..config.triage_settings import settings

logger = logging.getLogger(__name__)

class SyntheaGenerator:
    def __init__(self):
        self.output_path = settings.SYNTHEA_OUTPUT_PATH
        os.makedirs(self.output_path, exist_ok=True)
        
    def generate_patients(self, num_patients: int = 100) -> List[Dict[str, Any]]:
        logger.info(f"Generando {num_patients} pacientes sinteticos con Synthea")
        
        try:
            result = subprocess.run([
                "java", "-jar", "synthea.jar",
                "-p", str(num_patients),
                "--exporter.csv.export", "true",
                "--exporter.json.export", "true"
            ], cwd=self.output_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Error ejecutando Synthea: {result.stderr}")
                return self._generate_fallback_data(num_patients)
                
            cases = self._parse_synthea_output()
            return cases
            
        except FileNotFoundError:
            logger.warning("Synthea no encontrado, usando datos sinteticos internos")
            return self._generate_fallback_data(num_patients)
    
    def _generate_fallback_data(self, num_patients: int) -> List[Dict[str, Any]]:
        cases = []
        
        triage_distribution = {
            1: 0.05,
            2: 0.15,
            3: 0.40,
            4: 0.30,
            5: 0.10
        }
        
        symptom_database = {
            1: ["dolor toracico intenso", "dificultad respiratoria grave", "inconsciente", "hemorragia activa"],
            2: ["fiebre alta 40", "dolor abdominal intenso", "cefalea severa", "vomitos persistentes"],
            3: ["dolor moderado", "fiebre 38", "tos productiva", "dolor articular"],
            4: ["sintomas leves", "consulta control", "dolor leve", "resfrio comun"],
            5: ["molestia leve", "consulta administrativa", "sintomas cronicos", "sin urgencia"]
        }
        
        for _ in range(num_patients):
            rand = random.random()
            cumsum = 0
            nivel = 3
            for level, prob in triage_distribution.items():
                cumsum += prob
                if rand < cumsum:
                    nivel = level
                    break
                    
            symptoms = random.sample(symptom_database.get(nivel, symptom_database[3]), 
                                   random.randint(1, 3))
            
            vital_signs = self._generate_vital_signs(nivel)
            
            case = {
                "sintomas": symptoms,
                "vital_signs": vital_signs,
                "nivelPrioridad": nivel,
                "embarazo": random.random() < 0.1,
                "antecedentes": self._generate_antecedentes(),
                "comentario": " ".join(symptoms)
            }
            cases.append(case)
            
        logger.info(f"Generados {len(cases)} casos sinteticos")
        return cases
    
    def _generate_vital_signs(self, nivel: int) -> Dict[str, float]:
        base = {
            "temperature_c": 36.8,
            "heart_rate_bpm": 75,
            "respiratory_rate_bpm": 16,
            "systolic_bp_mmhg": 118,
            "diastolic_bp_mmhg": 76,
            "oxygen_saturation_pct": 98,
            "weight_kg": 70,
            "height_cm": 170
        }
        
        deviation = {
            1: 0.25,
            2: 0.15,
            3: 0.05,
            4: 0.02,
            5: 0.01
        }.get(nivel, 0.05)
        
        vital_signs = {}
        for key, value in base.items():
            if key in ["temperature_c", "heart_rate_bpm", "respiratory_rate_bpm"]:
                sign = 1 if random.random() > 0.5 else -1
                vital_signs[key] = round(value * (1 + sign * random.uniform(0, deviation)), 1)
            elif key in ["systolic_bp_mmhg", "diastolic_bp_mmhg"]:
                vital_signs[key] = int(value * (1 + random.uniform(-deviation, deviation)))
            else:
                vital_signs[key] = value if random.random() > deviation else value * (1 + random.uniform(-0.1, 0.1))
                
        return vital_signs
    
    def _generate_antecedentes(self) -> List[str]:
        antecedentes_pool = ["hipertension", "diabetes", "asma", "alergias", "cardiopatia"]
        num = random.randint(0, 2)
        return random.sample(antecedentes_pool, num) if num > 0 else []
    
    def _parse_synthea_output(self) -> List[Dict[str, Any]]:
        return self._generate_fallback_data(100)

synthea_generator = SyntheaGenerator()