from fastapi import APIRouter
import logging
import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
from app.core.features.team_stats_calculator import team_stats_calculator

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

router = APIRouter()
logger = logging.getLogger(__name__)

MODELS_PATH = "C:\\Users\\Manuel Alejandro\\Downloads\\Mike\\models"
os.makedirs(MODELS_PATH, exist_ok=True)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "ecibethistorical")

@router.post("/train/rf")
async def train_random_forest():
    logger.info("Iniciando entrenamiento de Random Forest")

    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        matches = list(db.historical_matches.find({
            "syncVersion": "kaggle_v1",
            "status": "Match Finished",
            "homeScore": {"$exists": True, "$ne": None},
            "awayScore": {"$exists": True, "$ne": None}
        }))

        logger.info(f"Total partidos Kaggle encontrados: {len(matches)}")

        if len(matches) < 100:
            return {
                "status": "error",
                "message": f"Se necesitan mas datos. Solo {len(matches)} partidos disponibles."
            }

        data = []
        skipped = 0
        for match in matches:
            home_team = match.get("homeTeam")
            away_team = match.get("awayTeam")
            season = match.get("season")

            if not home_team or not away_team or not season:
                skipped += 1
                continue

            home_stats = team_stats_calculator.get_team_stats(home_team, "", season)
            away_stats = team_stats_calculator.get_team_stats(away_team, "", season)

            home_goals = match.get("homeScore", 0)
            away_goals = match.get("awayScore", 0)

            if home_goals > away_goals:
                result = "HOME"
            elif home_goals < away_goals:
                result = "AWAY"
            else:
                result = "DRAW"

            data.append({
                "home_position": home_stats["position"],
                "away_position": away_stats["position"],
                "home_points_last5": home_stats["points_last5"],
                "away_points_last5": away_stats["points_last5"],
                "home_goals_avg": home_stats["goals_avg"],
                "away_goals_avg": away_stats["goals_avg"],
                "result": result
            })

        logger.info(f"Partidos procesados: {len(data)}, saltados: {skipped}")

        df = pd.DataFrame(data)

        feature_cols = ["home_position", "away_position", "home_points_last5", "away_points_last5", "home_goals_avg", "away_goals_avg"]
        X = df[feature_cols].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        y_home = (df["result"] == "HOME").astype(int)
        y_draw = (df["result"] == "DRAW").astype(int)
        y_away = (df["result"] == "AWAY").astype(int)

        rf_home = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf_home.fit(X_scaled, y_home)

        rf_draw = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf_draw.fit(X_scaled, y_draw)

        rf_away = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf_away.fit(X_scaled, y_away)

        joblib.dump(rf_home, os.path.join(MODELS_PATH, "rf_1x2_home.pkl"))
        joblib.dump(rf_draw, os.path.join(MODELS_PATH, "rf_1x2_draw.pkl"))
        joblib.dump(rf_away, os.path.join(MODELS_PATH, "rf_1x2_away.pkl"))
        joblib.dump(scaler, os.path.join(MODELS_PATH, "scaler.pkl"))

        logger.info(f"Modelos guardados usando {len(matches)} partidos")

        return {
            "status": "success",
            "message": "Modelos entrenados exitosamente",
            "models_saved": ["rf_1x2_home.pkl", "rf_1x2_draw.pkl", "rf_1x2_away.pkl", "scaler.pkl"],
            "samples_used": len(matches),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error entrenando Random Forest: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/train/status")
async def get_training_status():
    models_exist = all(os.path.exists(os.path.join(MODELS_PATH, f)) for f in ["rf_1x2_home.pkl", "rf_1x2_draw.pkl", "rf_1x2_away.pkl"])
    return {
        "status": "idle",
        "last_training": None,
        "models_available": models_exist
    }