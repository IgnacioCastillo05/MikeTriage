import logging
import numpy as np
from typing import Dict, Any, Optional
import joblib
import os

logger = logging.getLogger(__name__)

class XGBoostPredictor:
    def __init__(self, model_path: str = None):
        self.model = None
        if model_path and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                logger.info(f"XGBoost cargado desde {model_path}")
            except Exception as e:
                logger.warning(f"No se pudo cargar XGBoost: {e}")

    def predict(self, features: np.ndarray) -> Dict[str, float]:
        if self.model is None:
            return {"home": 0.44, "draw": 0.28, "away": 0.24}

        try:
            predictions = self.model.predict_proba(features)
            return {
                "home": float(predictions[0][1]),
                "draw": float(predictions[0][2]),
                "away": float(predictions[0][0])
            }
        except Exception as e:
            logger.error(f"Error en XGBoost: {e}")
            return {"home": 0.44, "draw": 0.28, "away": 0.24}