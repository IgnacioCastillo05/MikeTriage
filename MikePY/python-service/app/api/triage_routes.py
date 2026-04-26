from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime
from typing import Dict, Any
from ..ml.triage_predictor import triage_predictor
from ..ml.triage_trainer import triage_trainer
from ..data.triage_dataset_loader import triage_dataset_loader
from ..data.synthea_generator import synthea_generator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/predict/triage")
async def predict_triage(request: Dict[str, Any]):
    logger.info("Prediccion de triaje solicitada")

    try:
        triage_data = request.get("triage_data", {})
        vital_signs = request.get("vital_signs", {})

        if not triage_data:
            triage_data = request

        if vital_signs:
            triage_data["vital_signs"] = vital_signs

        if "sintomas" not in triage_data:
            transcript = triage_data.get("transcript", "")
            if transcript:
                triage_data["sintomas"] = [transcript]
                triage_data["comentario"] = transcript

        result = triage_predictor.predict(triage_data)

        nivel = result["nivel_triage"]
        descripcion = result["descripcion"]
        confianza = result["confianza"]
        probabilidades = result.get("probabilidades", {})
        probs = {f"nivel_{i}": probabilidades.get(f"nivel_{i}", 0.0) for i in range(1, 6)}

        return {
            "procedure_id": request.get("procedure_id"),
            "patient_cedula": request.get("patient_cedula"),
            "nivel_triage": nivel,
            "descripcion_triage": descripcion,
            "timestamp": datetime.utcnow().isoformat() + "Z",

            # Campos que necesita Triage
            "nivel_sugerido": nivel,
            "confianza": confianza,
            "comentarios": descripcion,
            "probabilidades": probs,
        }

    except Exception as e:
        logger.error(f"Error en prediccion de triaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train/triage")
async def train_triage():
    logger.info("Entrenamiento de modelo de triaje iniciado")

    try:
        fedmll_cases = triage_dataset_loader.load_fedmll_triage()
        synthea_cases = synthea_generator.generate_patients(500)
        all_cases = fedmll_cases + synthea_cases

        if len(all_cases) < 100:
            return {"status": "error", "message": f"Datos insuficientes: {len(all_cases)} casos"}

        X, y = triage_trainer.prepare_training_data(all_cases)
        result = triage_trainer.train(X, y)

        return {
            "status": "success",
            "message": "Modelo de triaje entrenado exitosamente",
            "metrics": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error entrenando modelo de triaje: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/triage/health")
async def triage_health():
    return {
        "status": "healthy",
        "model_loaded": triage_predictor.model is not None,
        "models_path": str(triage_trainer.models_path)
    }