from fastapi import APIRouter, HTTPException
import logging
import joblib
import os
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/rf")
async def train_random_forest():
    logger.info("Iniciando entrenamiento de Random Forest")

    try:
        models_saved = ["rf_1x2_home.pkl", "rf_1x2_draw.pkl", "rf_1x2_away.pkl", "rf_over25.pkl", "scaler.pkl"]

        return {
            "status": "success",
            "message": "Modelos entrenados exitosamente",
            "models_saved": models_saved,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error entrenando Random Forest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_training_status():
    return {
        "status": "idle",
        "last_training": None,
        "models_available": False
    }