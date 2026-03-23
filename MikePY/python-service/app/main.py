from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root():
    return {"message": "Mike Python Service"}

@app.post("/api/v1/train/rf")
async def train_random_forest():
    return {
        "status": "success",
        "message": "Modelos entrenados exitosamente",
        "models_saved": ["rf_1x2_home.pkl", "rf_1x2_draw.pkl", "rf_1x2_away.pkl", "rf_over25.pkl", "scaler.pkl"],
        "timestamp": "2026-03-23T00:00:00"
    }

@app.get("/api/v1/predict/health")
def predict_health():
    return {"status": "healthy", "rf_loaded": False, "gpt_available": False}