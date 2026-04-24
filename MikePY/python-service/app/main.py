
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api import triage_routes
from app.config.triage_settings import settings
from app.ml.triage_predictor import triage_predictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mike Triage Agent",
    description="Agente de IA para triaje medico basado en Random Forest",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage_routes.router, prefix="/api/v1", tags=["triage"])

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando Mike Triage Agent")
    loaded = triage_predictor.load()
    if loaded:
        logger.info("Modelo de triaje cargado correctamente")
    else:
        logger.warning("Modelo de triaje no encontrado. Use /api/v1/train/triage para entrenar")

@app.get("/")
async def root():
    return {
        "agent": "Mike",
        "version": "2.0.0",
        "context": "medical_triage",
        "status": "active"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": triage_predictor.model is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)