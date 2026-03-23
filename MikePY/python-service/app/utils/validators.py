import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def validate_match_data(data: Dict[str, Any]) -> bool:
    try:
        if 'event_id' in data and not data['event_id']:
            raise ValueError("event_id no puede estar vacío")

        if 'home_team' in data and not data['home_team']:
            raise ValueError("home_team no puede estar vacío")

        if 'away_team' in data and not data['away_team']:
            raise ValueError("away_team no puede estar vacío")

        if 'minute' in data:
            minute = data['minute']
            if minute < 0 or minute > 120:
                raise ValueError(f"minute inválido: {minute}")

        if 'home_score' in data and 'away_score' in data:
            if data['home_score'] < 0 or data['away_score'] < 0:
                raise ValueError("Los goles no pueden ser negativos")

        return True

    except Exception as e:
        logger.error(f"Error validando datos: {e}")
        raise