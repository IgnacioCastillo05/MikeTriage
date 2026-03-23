from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime

from app.api.models.request_models import PreMatchRequest, LiveUpdateRequest
from app.api.models.response_models import OddsResponse
from app.core.predictors.random_forest import RandomForestPredictor
from app.core.features.gpt_feature_engineer import GPTFeatureEngineer

router = APIRouter()
logger = logging.getLogger(__name__)

rf_predictor = RandomForestPredictor()
gpt_engineer = GPTFeatureEngineer()

@router.post("/predict/prematch", response_model=OddsResponse)
async def predict_prematch(request: PreMatchRequest):
    try:
        result = rf_predictor.predict(request.dict(), None)
        return result
    except Exception as e:
        logger.error(f"Error en predict_prematch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/live", response_model=OddsResponse)
async def predict_live(request: LiveUpdateRequest):
    try:
        result = rf_predictor.predict_live(request, None)
        return result
    except Exception as e:
        logger.error(f"Error en predict_live: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/health")
async def predict_health():
    return {
        "status": "healthy",
        "rf_loaded": False,
        "gpt_available": gpt_engineer.is_available()
    }