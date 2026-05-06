
import numpy as np
from typing import Dict, Any, List
import logging
from .symptom_encoder import symptom_encoder

logger = logging.getLogger(__name__)

class TriageFeatureExtractor:
    def __init__(self):
        self.symptom_encoder = symptom_encoder
        self.normal_ranges = {
            "temperature_c": (36.1, 37.2),
            "heart_rate_bpm": (60, 100),
            "respiratory_rate_bpm": (12, 20),
            "systolic_bp_mmhg": (90, 120),
            "diastolic_bp_mmhg": (60, 80),
            "oxygen_saturation_pct": (95, 100)
        }
        
    _FIXED_VITALS = [
        "temperature_c",
        "heart_rate_bpm",
        "respiratory_rate_bpm",
        "systolic_bp_mmhg",
        "diastolic_bp_mmhg",
        "oxygen_saturation_pct",
        "weight_kg",
        "height_cm",
    ]
        
    def extract_features(self, triage_data: Dict[str, Any]) -> np.ndarray:
        features = {}
        symptoms = triage_data.get("sintomas", [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]

        if self.symptom_encoder.vectorizer:
            symptom_vector = self.symptom_encoder.transform(symptoms)[0]
            for i, val in enumerate(symptom_vector):
                features[f"symptom_{i}"] = val
        else:
            features["symptom_count"] = len(symptoms)

        emergency_flags = self.symptom_encoder.extract_emergency_flags(symptoms)
        features.update(emergency_flags)

        vital_signs = triage_data.get("vital_signs", {})

        for vital in _FIXED_VITALS:
            value = vital_signs.get(vital, 0.0)
            features[vital] = value
            if vital in self.normal_ranges:
                min_norm, max_norm = self.normal_ranges[vital]
                if value < min_norm:
                    features[f"{vital}_anomaly"] = (min_norm - value) / min_norm
                elif value > max_norm:
                    features[f"{vital}_anomaly"] = (value - max_norm) / max_norm
                else:
                    features[f"{vital}_anomaly"] = 0.0

        hr = vital_signs.get("heart_rate_bpm", 0.0)
        rr = vital_signs.get("respiratory_rate_bpm", 1.0)
        sbp = vital_signs.get("systolic_bp_mmhg", 0.0)
        dbp = vital_signs.get("diastolic_bp_mmhg", 0.0)
        spo2 = vital_signs.get("oxygen_saturation_pct", 95.0)

        features["hr_rr_ratio"] = hr / max(rr, 1)
        features["map"] = (sbp + 2 * dbp) / 3
        features["pulse_pressure"] = sbp - dbp
        features["hypoxia_severity"] = max(0, 95 - spo2)

        features["embarazo"] = 1 if triage_data.get("embarazo", False) else 0
        features["num_antecedentes"] = len(triage_data.get("antecedentes", []))

        transcript = triage_data.get("comentario", "")
        features["transcript_length"] = len(transcript)
        features["transcript_words"] = len(transcript.split())

        feature_names = sorted(features.keys())
        feature_vector = np.array([features[name] for name in feature_names])
        return feature_vector.reshape(1, -1)
    
    def get_feature_names(self, triage_data: Dict[str, Any]) -> List[str]:
        features = {}
        symptoms = triage_data.get("sintomas", [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
            
        if self.symptom_encoder.vectorizer:
            symptom_vector = self.symptom_encoder.transform(symptoms)[0]
            for i in range(len(symptom_vector)):
                features[f"symptom_{i}"] = 0
                
        features.update(self.symptom_encoder.extract_emergency_flags(symptoms))
        
        vital_signs = triage_data.get("vital_signs", {})
        for vital in vital_signs.keys():
            features[f"{vital}"] = 0
            features[f"{vital}_anomaly"] = 0
            
        features["hr_rr_ratio"] = 0
        features["map"] = 0
        features["pulse_pressure"] = 0
        features["hypoxia_severity"] = 0
        features["embarazo"] = 0
        features["num_antecedentes"] = 0
        features["transcript_length"] = 0
        features["transcript_words"] = 0
        
        return sorted(features.keys())

triage_feature_extractor = TriageFeatureExtractor()