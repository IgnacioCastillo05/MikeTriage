import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

print("=== ENTRENANDO MIKE TRIAGE AGENT ===\n")

models_path = os.path.join("models", "triaje")
os.makedirs(models_path, exist_ok=True)

print("Generando datos sinteticos de entrenamiento...")

def generate_triage_data(n_samples=10000):
    X = []
    y = []
    
    for _ in range(n_samples):
        nivel = np.random.choice([1,2,3,4,5], p=[0.05, 0.15, 0.40, 0.30, 0.10])
        
        if nivel == 1:
            temp = np.random.uniform(39, 41)
            hr = np.random.uniform(120, 150)
            rr = np.random.uniform(25, 35)
            sbp = np.random.uniform(160, 200)
            spo2 = np.random.uniform(70, 89)
        elif nivel == 2:
            temp = np.random.uniform(38.5, 39.5)
            hr = np.random.uniform(100, 130)
            rr = np.random.uniform(20, 28)
            sbp = np.random.uniform(140, 170)
            spo2 = np.random.uniform(90, 94)
        elif nivel == 3:
            temp = np.random.uniform(37.5, 38.5)
            hr = np.random.uniform(80, 110)
            rr = np.random.uniform(16, 22)
            sbp = np.random.uniform(120, 150)
            spo2 = np.random.uniform(95, 97)
        elif nivel == 4:
            temp = np.random.uniform(36.5, 37.5)
            hr = np.random.uniform(60, 90)
            rr = np.random.uniform(12, 18)
            sbp = np.random.uniform(100, 130)
            spo2 = np.random.uniform(97, 99)
        else:
            temp = np.random.uniform(36, 37)
            hr = np.random.uniform(55, 75)
            rr = np.random.uniform(10, 14)
            sbp = np.random.uniform(90, 115)
            spo2 = np.random.uniform(98, 100)
        
        dbp = sbp - np.random.uniform(30, 50)
        weight = np.random.uniform(50, 100)
        height = np.random.uniform(150, 190)
        
        features = [
            temp, hr, rr, sbp, dbp, spo2, weight, height,
            np.random.randint(1, 8),
            np.random.randint(0, 3),
            np.random.randint(0, 2),
            np.random.randint(0, 2),
            np.random.randint(0, 2),
            np.random.randint(0, 2),
            np.random.randint(0, 2),
            abs(temp - 36.8) / 36.8,
            abs(hr - 75) / 75,
            abs(rr - 16) / 16,
            abs(sbp - 120) / 120,
            abs(spo2 - 98) / 98,
            hr / max(rr, 1),
            (sbp + 2*dbp)/3,
            sbp - dbp,
            max(0, 95 - spo2),
            np.random.randint(0, 2),
            np.random.randint(0, 3),
            np.random.randint(0, 100),
            np.random.randint(0, 20)
        ]
        
        while len(features) < 25:
            features.append(0)
        
        X.append(features[:25])
        y.append(nivel)
    
    return np.array(X), np.array(y)

X, y = generate_triage_data(10000)
print(f"Datos generados: {X.shape[0]} muestras, {X.shape[1]} features")

print("\nEntrenando modelo...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_scaled, y)

print("\nGuardando modelos...")
joblib.dump(model, os.path.join(models_path, "rf_triage.pkl"))
joblib.dump(scaler, os.path.join(models_path, "scaler_triage.pkl"))

accuracy = model.score(X_scaled, y)
print(f"\nEntrenamiento completado!")
print(f"Accuracy: {accuracy:.2f}")
print(f"Modelos guardados en: {models_path}")