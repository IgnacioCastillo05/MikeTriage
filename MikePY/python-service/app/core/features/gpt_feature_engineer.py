import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GPTFeatureEngineer:
    def __init__(self):
        self._available = False
        logger.info("GPTFeatureEngineer inicializado en modo demo")

    def is_available(self) -> bool:
        return self._available

    async def generate_prematch_features(self, match_data: Dict[str, Any]) -> Dict[str, float]:
        return {
            "momentum_score": 0.5,
            "psychological_advantage": 0.5,
            "injury_impact_score": 0.5,
            "h2h_psychological": 0.5,
            "match_importance": 0.5,
            "rest_quality": 0.5,
            "upset_potential": 0.5,
            "rivalry_intensity": 0.5,
            "home_advantage_boost": 0.5,
            "form_consistency": 0.5
        }

    async def generate_live_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        return {
            "momentum_shift": 0.5,
            "time_pressure": 0.5,
            "score_impact": 0.5,
            "comeback_probability": 0.5,
            "attacking_urgency": 0.5,
            "defensive_stability": 0.5,
            "event_impact": 0.5
        }