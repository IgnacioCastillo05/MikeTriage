from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import joblib
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(title="Mike Triage Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models_path = os.path.join("models", "triaje")
model_path = os.path.join(models_path, "rf_triage.pkl")
scaler_path = os.path.join(models_path, "scaler_triage.pkl")

model = None
scaler = None

class TriageRequest(BaseModel):
    sintomas: List[str]
    vital_signs: Dict[str, float]
    embarazo: Optional[bool] = False
    antecedentes: Optional[List[str]] = []
    comentario: Optional[str] = ""

class TriageResponse(BaseModel):
    nivel_triage: int
    descripcion: str
    confianza: float
    timestamp: str

def load_models():
    global model, scaler
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("Modelos cargados correctamente")
        return True
    else:
        print("Modelos no encontrados. Ejecute train.py primero")
        return False

def extract_features_25(data: dict) -> np.ndarray:
    vital = data.get("vital_signs", {})
    
    features = []
    features.append(vital.get("temperature_c", 36.5))
    features.append(vital.get("heart_rate_bpm", 75))
    features.append(vital.get("respiratory_rate_bpm", 16))
    features.append(vital.get("systolic_bp_mmhg", 120))
    features.append(vital.get("diastolic_bp_mmhg", 80))
    features.append(vital.get("oxygen_saturation_pct", 98))
    features.append(vital.get("weight_kg", 70))
    features.append(vital.get("height_cm", 170))
    
    num_symptoms = len(data.get("sintomas", []))
    features.append(min(num_symptoms, 10))
    
    symptoms_text = " ".join(data.get("sintomas", [])).lower()
    emergency_keywords = ["paro", "inconsciente", "convulsion", "hemorragia", "shock", "anafilaxia", "trauma", "quemadura"]
    keyword_count = sum(1 for kw in emergency_keywords if kw in symptoms_text)
    features.append(min(keyword_count, 5))
    
    features.append(1 if "dolor toracico" in symptoms_text or "dificultad respirar" in symptoms_text else 0)
    features.append(1 if "fiebre" in symptoms_text else 0)
    features.append(1 if "cefalea" in symptoms_text or "dolor cabeza" in symptoms_text else 0)
    features.append(1 if "vomito" in symptoms_text else 0)
    features.append(1 if "diarrea" in symptoms_text else 0)
    
    def deviation(val, normal_min, normal_max):
        if val < normal_min:
            return (normal_min - val) / normal_min
        elif val > normal_max:
            return (val - normal_max) / normal_max
        return 0
    
    features.append(deviation(vital.get("temperature_c", 36.5), 36.1, 37.2))
    features.append(deviation(vital.get("heart_rate_bpm", 75), 60, 100))
    features.append(deviation(vital.get("respiratory_rate_bpm", 16), 12, 20))
    features.append(deviation(vital.get("systolic_bp_mmhg", 120), 90, 120))
    features.append(deviation(vital.get("oxygen_saturation_pct", 98), 95, 100))
    
    hr = vital.get("heart_rate_bpm", 75)
    rr = vital.get("respiratory_rate_bpm", 16)
    features.append(hr / max(rr, 1))
    
    sbp = vital.get("systolic_bp_mmhg", 120)
    dbp = vital.get("diastolic_bp_mmhg", 80)
    features.append((sbp + 2 * dbp) / 3)
    features.append(sbp - dbp)
    
    spo2 = vital.get("oxygen_saturation_pct", 98)
    features.append(max(0, 95 - spo2))
    
    features.append(1 if data.get("embarazo", False) else 0)
    features.append(len(data.get("antecedentes", [])))
    
    transcript = data.get("comentario", "")
    features.append(len(transcript))
    features.append(len(transcript.split()))
    
    while len(features) < 25:
        features.append(0)
    
    return np.array(features[:25]).reshape(1, -1)

@app.on_event("startup")
async def startup_event():
    load_models()

@app.get("/")
async def root():
    return {"agent": "Mike", "version": "1.0.0", "status": "active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/triage", response_model=TriageResponse)
async def predict_triage(request: TriageRequest):
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Modelo no cargado")
    
    data = request.dict()
    features = extract_features_25(data)
    features_scaled = scaler.transform(features)
    
    prediction = model.predict(features_scaled)[0]
    probabilities = model.predict_proba(features_scaled)[0]
    confidence = float(max(probabilities))
    
    niveles = {1: "Emergencia", 2: "Muy Urgente", 3: "Urgente", 4: "Normal", 5: "No Urgente"}
    
    return TriageResponse(
        nivel_triage=int(prediction),
        descripcion=niveles[int(prediction)],
        confianza=round(confidence, 4),
        timestamp=datetime.utcnow().isoformat() + "Z"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)