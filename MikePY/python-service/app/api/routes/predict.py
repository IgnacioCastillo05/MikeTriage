from fastapi import APIRouter
import logging
import os
import joblib
import numpy as np
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from pathlib import Path
from app.core.features.team_stats_calculator import team_stats_calculator

router = APIRouter()
logger = logging.getLogger(__name__)

MODELS_PATH = os.getenv("MODELS_PATH", "C:\\Users\\Manuel Alejandro\\Downloads\\Mike\\models")

loaded_models = {}
scaler = None
feature_cols = None

def load_models():
    global loaded_models, scaler, feature_cols
    try:
        loaded_models['home'] = joblib.load(os.path.join(MODELS_PATH, "rf_1x2_home.pkl"))
        loaded_models['draw'] = joblib.load(os.path.join(MODELS_PATH, "rf_1x2_draw.pkl"))
        loaded_models['away'] = joblib.load(os.path.join(MODELS_PATH, "rf_1x2_away.pkl"))
        scaler = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
        feature_cols = joblib.load(os.path.join(MODELS_PATH, "feature_cols.pkl"))
        logger.info(f"Modelos cargados con {len(feature_cols)} features")
        return True
    except Exception as e:
        logger.warning(f"No se pudieron cargar modelos: {e}")
        return False

models_available = load_models()

def calculate_odds(probabilities: Dict[str, float]) -> Dict[str, float]:
    margin = 1.06
    total = sum(probabilities.values())
    if total > 0:
        normalized = {k: v / total for k, v in probabilities.items()}
    else:
        normalized = {"home": 0.33, "draw": 0.34, "away": 0.33}
    return {
        "home": round(margin / normalized["home"], 2),
        "draw": round(margin / normalized["draw"], 2),
        "away": round(margin / normalized["away"], 2)
    }

@router.post("/predict/force")
async def predict_force(request: Dict[str, Any]):
    logger.info(f"Request force: {request}")

    try:
        home_team = request.get("homeTeam") or request.get("home_team")
        away_team = request.get("awayTeam") or request.get("away_team")
        competition = request.get("competition", "English Premier League")
        season = request.get("season", "2015-2016")

        if not home_team or not away_team:
            raise ValueError(f"Faltan equipos: home={home_team}, away={away_team}")

        home_stats = team_stats_calculator.get_team_stats(home_team, competition, season)
        away_stats = team_stats_calculator.get_team_stats(away_team, competition, season)

        home_strength = home_stats.get("points", 10) / max(home_stats.get("matches_played", 1), 1)
        away_strength = away_stats.get("points", 10) / max(away_stats.get("matches_played", 1), 1)
        home_win_pct = home_stats.get("wins", 0) / max(home_stats.get("matches_played", 1), 1)
        away_win_pct = away_stats.get("wins", 0) / max(away_stats.get("matches_played", 1), 1)
        home_gd_avg = (home_stats.get("goals_scored", 0) - home_stats.get("goals_conceded", 0)) / max(home_stats.get("matches_played", 1), 1)
        away_gd_avg = (away_stats.get("goals_scored", 0) - away_stats.get("goals_conceded", 0)) / max(away_stats.get("matches_played", 1), 1)
        home_form_ratio = home_stats.get("points_last5", 5) / 15
        away_form_ratio = away_stats.get("points_last5", 5) / 15

        features_dict = {
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
            "win_pct_diff": home_win_pct - away_win_pct
        }

        features = np.array([[features_dict[col] for col in feature_cols]])

        if scaler is not None:
            features = scaler.transform(features)

        if models_available and 'home' in loaded_models:
            prob_home = float(loaded_models['home'].predict_proba(features)[0][1])
            prob_draw = float(loaded_models['draw'].predict_proba(features)[0][1])
            prob_away = float(loaded_models['away'].predict_proba(features)[0][1])
            reason = "Prediccion basada en Random Forest"
            logger.info(f"Probabilidades: home={prob_home}, draw={prob_draw}, away={prob_away}")
        else:
            prob_home = 0.44
            prob_draw = 0.28
            prob_away = 0.24
            reason = "Prediccion basada en valores por defecto"
            logger.warning("Usando valores por defecto - modelos no disponibles")

        total = prob_home + prob_draw + prob_away
        if total > 0:
            prob_home = prob_home / total
            prob_draw = prob_draw / total
            prob_away = prob_away / total

        odds = calculate_odds({"home": prob_home, "draw": prob_draw, "away": prob_away})

        return {
            "eventId": request.get("eventId") or request.get("event_id"),
            "externalId": request.get("externalId", "N/A"),
            "calculatedAt": datetime.utcnow().isoformat() + "Z",
            "markets": [
                {
                    "marketId": "1X2",
                    "marketName": "Resultado Final",
                    "marketType": "WIN_DRAW_WIN",
                    "selections": [
                        {
                            "selectionId": "HOME",
                            "selectionName": home_team,
                            "newOdds": odds["home"],
                            "probability": round(prob_home, 4),
                            "adjustmentFactor": 1.0
                        },
                        {
                            "selectionId": "DRAW",
                            "selectionName": "Empate",
                            "newOdds": odds["draw"],
                            "probability": round(prob_draw, 4),
                            "adjustmentFactor": 1.0
                        },
                        {
                            "selectionId": "AWAY",
                            "selectionName": away_team,
                            "newOdds": odds["away"],
                            "probability": round(prob_away, 4),
                            "adjustmentFactor": 1.0
                        }
                    ],
                    "reason": reason
                }
            ]
        }

    except Exception as e:
        logger.error(f"Error en predict_force: {e}", exc_info=True)
        return {
            "eventId": request.get("eventId") or request.get("event_id"),
            "externalId": "N/A",
            "calculatedAt": datetime.utcnow().isoformat() + "Z",
            "markets": [
                {
                    "marketId": "1X2",
                    "marketName": "Resultado Final",
                    "marketType": "WIN_DRAW_WIN",
                    "selections": [
                        {
                            "selectionId": "HOME",
                            "selectionName": request.get("homeTeam") or request.get("home_team", "Local"),
                            "newOdds": 2.10,
                            "probability": 0.44,
                            "adjustmentFactor": 1.0
                        },
                        {
                            "selectionId": "DRAW",
                            "selectionName": "Empate",
                            "newOdds": 3.40,
                            "probability": 0.28,
                            "adjustmentFactor": 1.0
                        },
                        {
                            "selectionId": "AWAY",
                            "selectionName": request.get("awayTeam") or request.get("away_team", "Visitante"),
                            "newOdds": 3.80,
                            "probability": 0.24,
                            "adjustmentFactor": 1.0
                        }
                    ],
                    "reason": "Error en prediccion - odds por defecto"
                }
            ]
        }

@router.post("/predict/prematch")
async def predict_prematch(request: Dict[str, Any]):
    logger.info(f"Request prematch: {request}")
    return await predict_force(request)

@router.get("/predict/health")
async def predict_health():
    return {
        "status": "healthy",
        "rf_loaded": models_available,
        "features_count": len(feature_cols) if feature_cols else 0
    }