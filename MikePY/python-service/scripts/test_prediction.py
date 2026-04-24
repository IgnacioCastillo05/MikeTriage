import sys
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

print("=== MIKE TRIAGE AGENT ===\n")

models_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "triaje")
model_path = os.path.join(models_path, "rf_triage.pkl")
scaler_path = os.path.join(models_path, "scaler_triage.pkl")

def extract_features_25(case):
    features = []
    vital = case.get("vital_signs", {})
    
    features.append(vital.get("temperature_c", 36.5))
    features.append(vital.get("heart_rate_bpm", 75))
    features.append(vital.get("respiratory_rate_bpm", 16))
    features.append(vital.get("systolic_bp_mmhg", 120))
    features.append(vital.get("diastolic_bp_mmhg", 80))
    features.append(vital.get("oxygen_saturation_pct", 98))
    features.append(vital.get("weight_kg", 70))
    features.append(vital.get("height_cm", 170))
    
    num_symptoms = len(case.get("sintomas", []))
    features.append(min(num_symptoms, 10))
    
    symptoms_text = " ".join(case.get("sintomas", [])).lower()
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
    
    features.append(1 if case.get("embarazo", False) else 0)
    features.append(len(case.get("antecedentes", [])))
    
    transcript = case.get("comentario", "")
    features.append(len(transcript))
    features.append(len(transcript.split()))
    
    while len(features) < 25:
        features.append(0)
    
    return np.array(features[:25]).reshape(1, -1)

if not os.path.exists(model_path):
    print("Modelo no encontrado. Entrenando modelo de demostracion...")
    
    X_train = np.random.rand(5000, 25)
    y_train = np.random.randint(1, 6, 5000)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_scaled, y_train)
    
    os.makedirs(models_path, exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"Modelo entrenado y guardado en {models_path}\n")
else:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("Modelo cargado correctamente\n")

test_cases = [
    {
        "sintomas": ["dolor toracico intenso", "dificultad para respirar"],
        "vital_signs": {
            "temperature_c": 37.5, "heart_rate_bpm": 120, "respiratory_rate_bpm": 28,
            "systolic_bp_mmhg": 160, "diastolic_bp_mmhg": 95, "oxygen_saturation_pct": 88,
            "weight_kg": 75, "height_cm": 175
        }
    },
    {
        "sintomas": ["fiebre", "tos", "dolor de garganta"],
        "vital_signs": {
            "temperature_c": 38.2, "heart_rate_bpm": 95, "respiratory_rate_bpm": 18,
            "systolic_bp_mmhg": 120, "diastolic_bp_mmhg": 80, "oxygen_saturation_pct": 97,
            "weight_kg": 70, "height_cm": 170
        }
    },
    {
        "sintomas": ["cefalea leve", "cansancio"],
        "vital_signs": {
            "temperature_c": 36.6, "heart_rate_bpm": 72, "respiratory_rate_bpm": 14,
            "systolic_bp_mmhg": 115, "diastolic_bp_mmhg": 75, "oxygen_saturation_pct": 99,
            "weight_kg": 65, "height_cm": 160
        }
    }
]

niveles = {1: "Emergencia", 2: "Muy Urgente", 3: "Urgente", 4: "Normal", 5: "No Urgente"}

for i, case in enumerate(test_cases, 1):
    print(f"Caso {i}:")
    print(f"Sintomas: {case['sintomas']}")
    print(f"Signos: T={case['vital_signs']['temperature_c']}C, FC={case['vital_signs']['heart_rate_bpm']}, SpO2={case['vital_signs']['oxygen_saturation_pct']}%")
    
    features = extract_features_25(case)
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    
    print(f"Nivel triaje: {prediction} - {niveles[prediction]}")
    print("-" * 40)