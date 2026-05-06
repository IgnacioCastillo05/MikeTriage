
import logging
import numpy as np
from typing import Dict, Any
import joblib
import os
from ..config.triage_settings import settings
from .feature_extractor import triage_feature_extractor
from .symptom_encoder import symptom_encoder

logger = logging.getLogger(__name__)

class TriagePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.models_path = settings.MODELS_PATH
        self.load()
        
    def load(self):
        model_path = os.path.join(self.models_path, "rf_triage.pkl")
        scaler_path = os.path.join(self.models_path, "scaler_triage.pkl")
        vectorizer_path = os.path.join(self.models_path, "vectorizer_triage.pkl")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            if os.path.exists(vectorizer_path):
                symptom_encoder.load(vectorizer_path)
                logger.info("Vectorizador de síntomas cargado correctamente")
            else:
                logger.warning("vectorizer_triage.pkl no encontrado - se usará symptom_count")
            logger.info("Modelo de triaje cargado correctamente")
            return True
        else:
            logger.warning("Modelo de triaje no encontrado")
            return False
    
    def predict(self, triage_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None:
            return self._fallback_prediction(triage_data)
            
        try:
            features = triage_feature_extractor.extract_features(triage_data)
            features_scaled = self.scaler.transform(features)
            
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            confidence = float(max(probabilities))
            
            return {
                "nivel_triage": int(prediction),
                "descripcion": settings.TRIAGE_LEVELS.get(int(prediction), "Desconocido"),
                "confianza": round(confidence, 4),
                "probabilidades": {
                    f"nivel_{i+1}": float(probabilities[i]) 
                    for i in range(len(probabilities))
                }
            }
            
        except Exception as e:
            logger.error(f"Error en prediccion: {e}")
            return self._fallback_prediction(triage_data)
    
    def _fallback_prediction(self, triage_data: Dict[str, Any]) -> Dict[str, Any]:
        nivel = 3
        vital_signs = triage_data.get("vital_signs", {})
        
        for vital, value in vital_signs.items():
            if vital in settings.CRITICAL_THRESHOLDS:
                thresholds = settings.CRITICAL_THRESHOLDS[vital]
                if value < thresholds["min"] or value > thresholds["max"]:
                    nivel = 1
                    
        symptoms = triage_data.get("sintomas", [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]
            
        flags = symptom_encoder.extract_emergency_flags(symptoms)
        if flags["has_nivel1_keyword"]:
            nivel = 1
        elif flags["has_nivel2_keyword"] and nivel > 2:
            nivel = 2
            
        return {
            "nivel_triage": nivel,
            "descripcion": settings.TRIAGE_LEVELS.get(nivel, "Desconocido"),
            "confianza": 0.5,
            "probabilidades": {},
            "fallback": True
        }

triage_predictor = TriagePredictor()