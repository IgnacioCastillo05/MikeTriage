
import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from datetime import datetime
from typing import Dict, Any, List
from ..config.triage_settings import settings
from .symptom_encoder import symptom_encoder
from .feature_extractor import triage_feature_extractor

logger = logging.getLogger(__name__)

class TriageTrainer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = None
        self.models_path = settings.MODELS_PATH
        
    def prepare_training_data(self, cases: List[Dict[str, Any]]) -> tuple:
        all_symptoms_text = []
        for case in cases:
            symptoms = case.get("sintomas", [])
            if isinstance(symptoms, list):
                all_symptoms_text.append(" ".join(symptoms))
            elif isinstance(symptoms, str):
                all_symptoms_text.append(symptoms)
        
        if all_symptoms_text:
            symptom_encoder.fit(all_symptoms_text)
            logger.info(f"Vectorizador ajustado con {len(all_symptoms_text)} muestras")

        features_list = []
        labels = []
        
        for case in cases:
            try:
                feature_vector = triage_feature_extractor.extract_features(case)
                features_list.append(feature_vector.flatten())
                nivel_prioridad = case.get("nivelPrioridad", case.get("triage_data", {}).get("nivelPrioridad"))
                if nivel_prioridad:
                    labels.append(int(nivel_prioridad))
            except Exception as e:
                logger.warning(f"Error procesando caso: {e}")
                continue
                
        if not features_list:
            raise ValueError("No se pudieron procesar casos de entrenamiento")
            
        X = np.array(features_list)
        y = np.array(labels)
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        logger.info(f"Iniciando entrenamiento con {X.shape[0]} muestras, {X.shape[1]} features")
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight='balanced',
            min_samples_split=5,
            min_samples_leaf=2
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        
        train_acc = self.model.score(X_train, y_train)
        val_acc = self.model.score(X_val, y_val)
        
        y_pred = self.model.predict(X_val)
        report = classification_report(y_val, y_pred, output_dict=True)
        
        logger.info(f"Train accuracy: {train_acc:.3f}, Validation accuracy: {val_acc:.3f}")
        
        os.makedirs(self.models_path, exist_ok=True)
        
        joblib.dump(self.model, os.path.join(self.models_path, "rf_triage.pkl"))
        joblib.dump(self.scaler, os.path.join(self.models_path, "scaler_triage.pkl"))
        
        if symptom_encoder.vectorizer:
            vectorizer_path = os.path.join(self.models_path, "vectorizer_triage.pkl")
            symptom_encoder.save(vectorizer_path)
            logger.info(f"Vectorizador guardado en {vectorizer_path}")
        
        return {
            "train_accuracy": train_acc,
            "validation_accuracy": val_acc,
            "classification_report": report,
            "samples_used": X.shape[0],
            "features_count": X.shape[1]
        }
    
    def load(self):
        model_path = os.path.join(self.models_path, "rf_triage.pkl")
        scaler_path = os.path.join(self.models_path, "scaler_triage.pkl")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            logger.info(f"Modelo cargado desde {model_path}")
            return True
        else:
            logger.warning("Modelos no encontrados")
            return False

triage_trainer = TriageTrainer()