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

router = APIRouter()  # <--- ESTA LÍNEA ES OBLIGATORIA

logger = logging.getLogger(__name__)

MODELS_PATH = "C:\\Users\\Manuel Alejandro\\Downloads\\Mike\\models"

loaded_models = {}
scaler = None

def load_models():
    global loaded_models, scaler
    try:
        loaded_models['home'] = joblib.load(os.path.join(MODELS_PATH, "rf_1x2_home.pkl"))
        loaded_models['draw'] = joblib.load(os.path.join(MODELS_PATH, "rf_1x2_draw.pkl"))
        loaded_models['away'] = joblib.load(os.path.join(MODELS_PATH, "rf_1x2_away.pkl"))
        scaler = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
        logger.info("Modelos cargados correctamente")
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

@router.post("/predict/prematch")
async def predict_prematch(request: Dict[str, Any]):
    logger.info(f"Request recibida: {request}")

    try:
        home_team = request.get("home_team")
        away_team = request.get("away_team")
        competition = request.get("competition", "English Premier League")
        season = request.get("season", "2015-2016")

        home_stats = team_stats_calculator.get_team_stats(home_team, competition, season)
        away_stats = team_stats_calculator.get_team_stats(away_team, competition, season)
        h2h_stats = team_stats_calculator.get_h2h_stats(home_team, away_team, competition, season)

        logger.info(f"Estadisticas de {home_team}: pos={home_stats['position']}, pts_ult5={home_stats['points_last5']}, goles_avg={home_stats['goals_avg']}, forma={home_stats['form']}")
        logger.info(f"Estadisticas de {away_team}: pos={away_stats['position']}, pts_ult5={away_stats['points_last5']}, goles_avg={away_stats['goals_avg']}, forma={away_stats['form']}")
        logger.info(f"H2H: {home_team} gana={h2h_stats['home_wins']}, empates={h2h_stats['draws']}, {away_team} gana={h2h_stats['away_wins']}")

        features = np.array([
            home_stats["position"],
            away_stats["position"],
            home_stats["points_last5"],
            away_stats["points_last5"],
            home_stats["goals_avg"],
            away_stats["goals_avg"]
        ]).reshape(1, -1)

        if scaler is not None:
            features = scaler.transform(features)

        if models_available and 'home' in loaded_models:
            prob_home = float(loaded_models['home'].predict_proba(features)[0][1])
            prob_draw = float(loaded_models['draw'].predict_proba(features)[0][1])
            prob_away = float(loaded_models['away'].predict_proba(features)[0][1])
            reason = "Prediccion basada en Random Forest"
        else:
            prob_home = 0.44
            prob_draw = 0.28
            prob_away = 0.24
            reason = "Prediccion basada en valores por defecto"

        total = prob_home + prob_draw + prob_away
        if total > 0:
            prob_home = prob_home / total
            prob_draw = prob_draw / total
            prob_away = prob_away / total

        odds = calculate_odds({"home": prob_home, "draw": prob_draw, "away": prob_away})

        return {
            "eventId": request.get("event_id"),
            "externalId": request.get("external_id", "N/A"),
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
        logger.error(f"Error en predict_prematch: {e}", exc_info=True)
        return {
            "eventId": request.get("event_id"),
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
                            "selectionName": request.get("home_team"),
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
                            "selectionName": request.get("away_team"),
                            "newOdds": 3.80,
                            "probability": 0.24,
                            "adjustmentFactor": 1.0
                        }
                    ],
                    "reason": "Error en prediccion - odds por defecto"
                }
            ]
        }

@router.post("/predict/live")
async def predict_live(request: Dict[str, Any]):
    try:
        home_team = request.get("home_team")
        away_team = request.get("away_team")
        competition = request.get("competition", "English Premier League")
        season = request.get("season", "2015-2016")
        minute = request.get("minute", 0)
        home_score = request.get("home_score", 0)
        away_score = request.get("away_score", 0)

        home_stats = team_stats_calculator.get_team_stats(home_team, competition, season)
        away_stats = team_stats_calculator.get_team_stats(away_team, competition, season)

        features = np.array([
            home_stats["position"],
            away_stats["position"],
            home_stats["points_last5"],
            away_stats["points_last5"],
            home_stats["goals_avg"],
            away_stats["goals_avg"]
        ]).reshape(1, -1)

        if scaler is not None:
            features = scaler.transform(features)

        if models_available and 'home' in loaded_models:
            prob_home = float(loaded_models['home'].predict_proba(features)[0][1])
            prob_draw = float(loaded_models['draw'].predict_proba(features)[0][1])
            prob_away = float(loaded_models['away'].predict_proba(features)[0][1])
        else:
            prob_home = 0.44
            prob_draw = 0.28
            prob_away = 0.24

        time_factor = 1.0 + (minute / 90) * 0.3

        if home_score > away_score:
            prob_home = prob_home * time_factor
        elif away_score > home_score:
            prob_away = prob_away * time_factor
        else:
            prob_draw = prob_draw * (1 + (minute / 90) * 0.15)

        total = prob_home + prob_draw + prob_away
        if total > 0:
            prob_home = prob_home / total
            prob_draw = prob_draw / total
            prob_away = prob_away / total

        odds = calculate_odds({"home": prob_home, "draw": prob_draw, "away": prob_away})

        return {
            "eventId": request.get("event_id"),
            "externalId": request.get("external_id", "N/A"),
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
                    "reason": f"Prediccion en vivo minuto {minute}"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error en predict_live: {e}")
        return {
            "eventId": request.get("event_id"),
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
                            "selectionName": request.get("home_team"),
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
                            "selectionName": request.get("away_team"),
                            "newOdds": 3.80,
                            "probability": 0.24,
                            "adjustmentFactor": 1.0
                        }
                    ],
                    "reason": "Error en prediccion - odds por defecto"
                }
            ]
        }

@router.get("/predict/health")
async def predict_health():
    return {
        "status": "healthy",
        "rf_loaded": models_available,
        "gpt_available": False
    }