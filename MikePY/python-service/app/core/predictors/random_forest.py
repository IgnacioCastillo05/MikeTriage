import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RandomForestPredictor:
    def __init__(self):
        self.models_loaded = False
        logger.info("RandomForestPredictor inicializado en modo demo")

    def extract_traditional_features(self, match_data: Dict, live_data: Optional[Dict] = None) -> Dict:
        features = {
            'home_points_last5': match_data.get('home_points_last5', 7.5) / 15,
            'away_points_last5': match_data.get('away_points_last5', 7.5) / 15,
            'home_goals_last5': min(match_data.get('home_goals_last5', 5) / 15, 1),
            'away_goals_last5': min(match_data.get('away_goals_last5', 5) / 15, 1),
            'home_position_norm': 1 - (match_data.get('home_position', 10) / 20),
            'away_position_norm': 1 - (match_data.get('away_position', 10) / 20),
            'position_diff': (match_data.get('away_position', 10) - match_data.get('home_position', 10)) / 20,
            'home_goals_avg': min(match_data.get('home_goals_avg', 1.5) / 4, 1),
            'away_goals_avg': min(match_data.get('away_goals_avg', 1.5) / 4, 1),
            'h2h_home_wins': match_data.get('h2h_home_wins', 0) / 10,
            'h2h_draws': match_data.get('h2h_draws', 0) / 10,
            'h2h_away_wins': match_data.get('h2h_away_wins', 0) / 10,
            'days_rest_home': min(match_data.get('days_rest_home', 7) / 14, 1),
            'days_rest_away': min(match_data.get('days_rest_away', 7) / 14, 1),
            'home_advantage': 1 if not match_data.get('neutral_venue', False) else 0,
            'injuries_count': min(len(match_data.get('home_injuries', [])) + len(match_data.get('away_injuries', [])), 5) / 5,
        }

        if live_data:
            features.update({
                'minute': live_data.get('minute', 0) / 90,
                'time_remaining': (90 - live_data.get('minute', 0)) / 90,
                'home_score': live_data.get('home_score', 0) / 5,
                'away_score': live_data.get('away_score', 0) / 5,
                'goal_difference': (live_data.get('home_score', 0) - live_data.get('away_score', 0)) / 5,
                'is_home_winning': 1 if live_data.get('home_score', 0) > live_data.get('away_score', 0) else 0,
                'is_away_winning': 1 if live_data.get('away_score', 0) > live_data.get('home_score', 0) else 0,
                'is_draw': 1 if live_data.get('home_score', 0) == live_data.get('away_score', 0) else 0,
                'total_goals': min((live_data.get('home_score', 0) + live_data.get('away_score', 0)) / 5, 1),
            })

        return features

    def predict(self, match_data: Dict, gpt_features: Optional[Dict] = None) -> Dict:
        features = self.extract_traditional_features(match_data)

        if gpt_features:
            for key, value in gpt_features.items():
                if isinstance(value, (int, float)):
                    features[key] = value

        probs = {
            'home': 0.45,
            'draw': 0.25,
            'away': 0.30
        }

        margin = 1.06
        odds = {
            'home': round(margin / probs['home'], 2),
            'draw': round(margin / probs['draw'], 2),
            'away': round(margin / probs['away'], 2),
        }

        return {
            'event_id': match_data.get('event_id', ''),
            'calculated_at': datetime.utcnow(),
            'markets': self._format_markets(odds, probs, match_data),
            'features_used': features
        }

    def predict_live(self, request, gpt_features: Optional[Dict] = None) -> Dict:
        match_data = getattr(request, 'pre_match_features', {})
        live_data = {
            'minute': request.minute,
            'home_score': request.home_score,
            'away_score': request.away_score
        }

        features = self.extract_traditional_features(match_data, live_data)

        if gpt_features:
            for key, value in gpt_features.items():
                if isinstance(value, (int, float)):
                    features[key] = value

        probs = {
            'home': 0.45,
            'draw': 0.25,
            'away': 0.30
        }

        margin = 1.06
        odds = {
            'home': round(margin / probs['home'], 2),
            'draw': round(margin / probs['draw'], 2),
            'away': round(margin / probs['away'], 2),
        }

        return {
            'event_id': request.event_id,
            'calculated_at': datetime.utcnow(),
            'markets': self._format_markets(odds, probs, match_data),
            'features_used': features
        }

    def _format_markets(self, odds: Dict, probs: Dict, match_data: Dict) -> list:
        markets = []

        markets.append({
            'market_id': '1X2',
            'market_name': 'Resultado Final',
            'market_type': 'WIN_DRAW_WIN',
            'selections': [
                {
                    'selection_id': 'HOME',
                    'selection_name': match_data.get('home_team', 'Local'),
                    'new_odds': odds['home'],
                    'probability': probs['home'],
                    'adjustment_factor': 1.0
                },
                {
                    'selection_id': 'DRAW',
                    'selection_name': 'Empate',
                    'new_odds': odds['draw'],
                    'probability': probs['draw'],
                    'adjustment_factor': 1.0
                },
                {
                    'selection_id': 'AWAY',
                    'selection_name': match_data.get('away_team', 'Visitante'),
                    'new_odds': odds['away'],
                    'probability': probs['away'],
                    'adjustment_factor': 1.0
                }
            ]
        })

        return markets