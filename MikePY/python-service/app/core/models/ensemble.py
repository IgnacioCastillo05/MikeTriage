import logging
import numpy as np
from typing import Dict, Any, List
from sklearn.linear_model import LogisticRegression
import joblib

logger = logging.getLogger(__name__)

class EnsemblePredictor:
    def __init__(self):
        self.meta_model = None
        self.weights = {"rf": 0.4, "xgb": 0.35, "nn": 0.25}

    def combine_predictions(self, predictions: List[Dict[str, float]]) -> Dict[str, float]:
        combined = {"home": 0.0, "draw": 0.0, "away": 0.0}

        for pred, weight in zip(predictions, self.weights.values()):
            combined["home"] += pred.get("home", 0.33) * weight
            combined["draw"] += pred.get("draw", 0.34) * weight
            combined["away"] += pred.get("away", 0.33) * weight

        return combined

    def train_meta_model(self, base_predictions: np.ndarray, y_true: np.ndarray) -> None:
        self.meta_model = LogisticRegression()
        self.meta_model.fit(base_predictions, y_true)
        logger.info("Meta-modelo entrenado correctamente")