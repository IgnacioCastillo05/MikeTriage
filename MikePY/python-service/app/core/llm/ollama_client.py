import logging
import httpx
import json
import re
from typing import Dict, Any, Optional
from app.config.settings import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.available = False
        self._check_availability()

    def _check_availability(self):
        try:
            response = httpx.get(f"{self.url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                self.available = True
                logger.info(f"Ollama disponible en {self.url}, modelo: {self.model}")
            else:
                logger.warning("Ollama no responde")
        except Exception as e:
            logger.warning(f"Ollama no disponible: {e}")

    async def get_prediction(self, home_team: str, away_team: str) -> Optional[Dict[str, float]]:
        if not self.available:
            return None

        prompt = f"""Analiza el partido entre {home_team} y {away_team}. 
Devuelve SOLO un JSON con las probabilidades de victoria local, empate y visitante.
Formato: {{"home": 0.45, "draw": 0.25, "away": 0.30}}
Las probabilidades deben sumar 1.0.
Considera forma reciente, enfrentamientos directos y ventaja local."""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=30.0
                )
                result = response.json()
                text = result.get("response", "")

                json_match = re.search(r'\{[^}]+\}', text)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Error en Ollama: {e}")

        return None

ollama_client = OllamaClient()