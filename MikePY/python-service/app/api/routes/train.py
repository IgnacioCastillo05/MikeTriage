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

MODELS_PATH = os.getenv("MODELS_PATH", "C:\\Users\\Manuel Alejandro\\Downloads\\Mike\\models")
os.makedirs(MODELS_PATH, exist_ok=True)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "ecibethistorical")

@router.post("/train/rf")
async def train_random_forest():
    logger.info("Iniciando entrenamiento de Random Forest - CORREGIDO")

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
        no_stats_count = 0

        for match in matches:
            home_team = match.get("homeTeam")
            away_team = match.get("awayTeam")
            season = match.get("season")

            if not home_team or not away_team or not season:
                skipped += 1
                continue

            home_stats = team_stats_calculator.get_team_stats(home_team, "", season)
            away_stats = team_stats_calculator.get_team_stats(away_team, "", season)

            if home_stats.get("matches_played", 0) < 3 or away_stats.get("matches_played", 0) < 3:
                no_stats_count += 1
                continue

            home_goals = match.get("homeScore", 0)
            away_goals = match.get("awayScore", 0)

            if home_goals > away_goals:
                result = "HOME"
            elif home_goals < away_goals:
                result = "AWAY"
            else:
                result = "DRAW"

            home_strength = home_stats.get("points", 10) / max(home_stats.get("matches_played", 1), 1)
            away_strength = away_stats.get("points", 10) / max(away_stats.get("matches_played", 1), 1)
            home_win_pct = home_stats.get("wins", 0) / max(home_stats.get("matches_played", 1), 1)
            away_win_pct = away_stats.get("wins", 0) / max(away_stats.get("matches_played", 1), 1)
            home_gd_avg = (home_stats.get("goals_scored", 0) - home_stats.get("goals_conceded", 0)) / max(home_stats.get("matches_played", 1), 1)
            away_gd_avg = (away_stats.get("goals_scored", 0) - away_stats.get("goals_conceded", 0)) / max(away_stats.get("matches_played", 1), 1)
            home_form_ratio = home_stats.get("points_last5", 5) / 15
            away_form_ratio = away_stats.get("points_last5", 5) / 15

            data.append({
                "home_position": home_stats["position"],
                "away_position": away_stats["position"],
                "home_points_last5": home_stats["points_last5"],
                "away_points_last5": away_stats["points_last5"],
                "home_goals_avg": home_stats["goals_avg"],
                "away_goals_avg": away_stats["goals_avg"],
                "home_strength": home_strength,
                "away_strength": away_strength,
                "home_win_pct": home_win_pct,
                "away_win_pct": away_win_pct,
                "home_gd_avg": home_gd_avg,
                "away_gd_avg": away_gd_avg,
                "home_form_ratio": home_form_ratio,
                "away_form_ratio": away_form_ratio,
                "strength_diff": home_strength - away_strength,
                "position_diff": home_stats["position"] - away_stats["position"],
                "form_diff": home_stats["points_last5"] - away_stats["points_last5"],
                "win_pct_diff": home_win_pct - away_win_pct,
                "result": result
            })

        logger.info(f"Partidos procesados: {len(data)}, saltados: {skipped}, sin estadisticas: {no_stats_count}")

        if len(data) < 100:
            return {
                "status": "error",
                "message": f"Datos insuficientes. Solo {len(data)} partidos validos."
            }

        df = pd.DataFrame(data)

        feature_cols = [
            "home_position", "away_position",
            "home_points_last5", "away_points_last5",
            "home_goals_avg", "away_goals_avg",
            "home_strength", "away_strength",
            "home_win_pct", "away_win_pct",
            "home_gd_avg", "away_gd_avg",
            "home_form_ratio", "away_form_ratio",
            "strength_diff", "position_diff", "form_diff", "win_pct_diff"
        ]

        X = df[feature_cols].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        y_home = (df["result"] == "HOME").astype(int)
        y_draw = (df["result"] == "DRAW").astype(int)
        y_away = (df["result"] == "AWAY").astype(int)

        home_count = y_home.sum()
        draw_count = y_draw.sum()
        away_count = y_away.sum()
        logger.info(f"Distribucion: HOME={home_count}, DRAW={draw_count}, AWAY={away_count}")

        rf_home = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight='balanced',
            min_samples_split=5,
            min_samples_leaf=2
        )
        rf_home.fit(X_scaled, y_home)

        rf_draw = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight='balanced',
            min_samples_split=5,
            min_samples_leaf=2
        )
        rf_draw.fit(X_scaled, y_draw)

        rf_away = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            random_state=42,
            class_weight='balanced',
            min_samples_split=5,
            min_samples_leaf=2
        )
        rf_away.fit(X_scaled, y_away)

        joblib.dump(rf_home, os.path.join(MODELS_PATH, "rf_1x2_home.pkl"))
        joblib.dump(rf_draw, os.path.join(MODELS_PATH, "rf_1x2_draw.pkl"))
        joblib.dump(rf_away, os.path.join(MODELS_PATH, "rf_1x2_away.pkl"))
        joblib.dump(scaler, os.path.join(MODELS_PATH, "scaler.pkl"))
        joblib.dump(feature_cols, os.path.join(MODELS_PATH, "feature_cols.pkl"))

        train_acc_home = rf_home.score(X_scaled, y_home)
        train_acc_draw = rf_draw.score(X_scaled, y_draw)
        train_acc_away = rf_away.score(X_scaled, y_away)

        logger.info(f"Accuracy entrenamiento - HOME: {train_acc_home:.3f}, DRAW: {train_acc_draw:.3f}, AWAY: {train_acc_away:.3f}")

        return {
            "status": "success",
            "message": "Modelos entrenados exitosamente",
            "models_saved": ["rf_1x2_home.pkl", "rf_1x2_draw.pkl", "rf_1x2_away.pkl", "scaler.pkl", "feature_cols.pkl"],
            "samples_used": len(data),
            "features_used": feature_cols,
            "distribution": {"home": int(home_count), "draw": int(draw_count), "away": int(away_count)},
            "train_accuracy": {"home": train_acc_home, "draw": train_acc_draw, "away": train_acc_away},
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