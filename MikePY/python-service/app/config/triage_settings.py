
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

class TriageSettings:
    TRIAGE_LEVELS = {
        1: "Emergencia - Rojo",
        2: "Muy Urgente - Naranja",
        3: "Urgente - Amarillo",
        4: "Normal - Verde",
        5: "No Urgente - Azul"
    }
    
    VITAL_SIGNS_RANGES = {
        "temperature_c": (36.1, 37.2),
        "heart_rate_bpm": (60, 100),
        "respiratory_rate_bpm": (12, 20),
        "systolic_bp_mmhg": (90, 120),
        "diastolic_bp_mmhg": (60, 80),
        "oxygen_saturation_pct": (95, 100)
    }
    
    CRITICAL_THRESHOLDS = {
        "temperature_c": {"min": 35.0, "max": 39.0},
        "heart_rate_bpm": {"min": 40, "max": 140},
        "respiratory_rate_bpm": {"min": 8, "max": 30},
        "systolic_bp_mmhg": {"min": 70, "max": 180},
        "oxygen_saturation_pct": {"min": 85, "max": 100}
    }
    
    MODELS_PATH = os.getenv("TRIAGE_MODELS_PATH", 
                           str(Path(__file__).resolve().parent.parent.parent / "models" / "triaje"))
    
    MIMIC_PROJECT_ID = os.getenv("MIMIC_PROJECT_ID", "")
    MIMIC_DATASET_ID = os.getenv("MIMIC_DATASET_ID", "physionet-data.mimiciv")
    
    SYNTHEA_OUTPUT_PATH = os.getenv("SYNTHEA_OUTPUT_PATH", 
                                    str(Path(__file__).resolve().parent.parent.parent / "data" / "synthetic"))
    
    CLASSIFIER_API_KEY = os.getenv("CLASSIFIER_API_KEY", "")

settings = TriageSettings()
