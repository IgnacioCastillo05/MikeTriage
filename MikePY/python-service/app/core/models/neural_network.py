import logging
import numpy as np
from typing import Dict, Any, Optional
from tensorflow import keras
from tensorflow.keras import layers
import joblib

logger = logging.getLogger(__name__)

class NeuralNetworkPredictor:
    def __init__(self, model_path: str = None):
        self.model = None
        if model_path:
            try:
                self.model = keras.models.load_model(model_path)
                logger.info(f"Red neuronal cargada desde {model_path}")
            except Exception as e:
                logger.warning(f"No se pudo cargar red neuronal: {e}")

    def predict(self, features: np.ndarray) -> Dict[str, float]:
        if self.model is None:
            return {"home": 0.44, "draw": 0.28, "away": 0.24}

        try:
            predictions = self.model.predict(features)
            return {
                "home": float(predictions[0][0]),
                "draw": float(predictions[0][1]),
                "away": float(predictions[0][2])
            }
        except Exception as e:
            logger.error(f"Error en predicción de red neuronal: {e}")
            return {"home": 0.44, "draw": 0.28, "away": 0.24}

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100) -> None:
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(3, activation='softmax')
        ])

        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        model.fit(X, y, epochs=epochs, batch_size=32, validation_split=0.2, verbose=1)
        self.model = model
        logger.info("Red neuronal entrenada correctamente")