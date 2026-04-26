
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SymptomEncoder:
    def __init__(self, model_path: str = None):
        self.vectorizer = None
        self.model_path = model_path
        self.emergency_keywords = {
            "nivel_1": [
                "paro cardiaco", "respiratorio", "inconsciente", "convulsiones",
                "hemorragia masiva", "shock", "anafilaxia", "ahogamiento",
                "trauma grave", "quemadura grave", "intoxicacion grave"
            ],
            "nivel_2": [
                "dolor toracico", "disnea", "cefalea intensa", "fiebre alta",
                "convulsion", "hemiplejia", "hemorragia", "vomito persistente"
            ]
        }
        
    def fit(self, symptoms_list: List[str]):
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2),
            stop_words='spanish'
        )
        self.vectorizer.fit(symptoms_list)
        logger.info(f"Vectorizador entrenado con {len(self.vectorizer.get_feature_names_out())} features")
        
    def transform(self, symptoms: List[str]) -> np.ndarray:
        if self.vectorizer is None:
            raise ValueError("Vectorizador no entrenado")
        if isinstance(symptoms, list):
            text = " ".join(symptoms)
        else:
            text = symptoms
        return self.vectorizer.transform([text]).toarray()
    
    def extract_emergency_flags(self, symptoms: List[str]) -> Dict[str, int]:
        text = " ".join(symptoms).lower()
        flags = {
            "has_nivel1_keyword": 0,
            "has_nivel2_keyword": 0,
            "num_keywords": 0
        }
        for kw in self.emergency_keywords["nivel_1"]:
            if kw in text:
                flags["has_nivel1_keyword"] = 1
                flags["num_keywords"] += 1
        for kw in self.emergency_keywords["nivel_2"]:
            if kw in text:
                flags["has_nivel2_keyword"] = 1
                flags["num_keywords"] += 1
        return flags
    
    def save(self, path: str):
        if self.vectorizer:
            joblib.dump(self.vectorizer, path)
            logger.info(f"Vectorizador guardado en {path}")
    
    def load(self, path: str):
        self.vectorizer = joblib.load(path)
        logger.info(f"Vectorizador cargado desde {path}")

symptom_encoder = SymptomEncoder()
