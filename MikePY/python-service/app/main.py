from fastapi import FastAPI
from app.api.routes import predict, train, kaggle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mike Python Service", version="2.0.0")

app.include_router(predict.router, prefix="/api/v1", tags=["predictions"])
app.include_router(train.router, prefix="/api/v1", tags=["training"])
app.include_router(kaggle.router, prefix="/api/v1/kaggle", tags=["kaggle"])

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "mike-python",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    return {
        "service": "Mike Python Service",
        "version": "2.0.0",
        "endpoints": [
            "/health",
            "/api/v1/predict/prematch",
            "/api/v1/predict/live",
            "/api/v1/predict/health",
            "/api/v1/train/rf",
            "/api/v1/train/status",
            "/api/v1/kaggle/import",
            "/api/v1/kaggle/status"
        ]
    }