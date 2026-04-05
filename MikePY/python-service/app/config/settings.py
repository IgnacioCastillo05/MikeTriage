import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    # MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "ecibethistorical")

    # SportDB
    SPORTDB_API_KEY = os.getenv("SPORTDB_API_KEY", "3")
    SPORTDB_BASE_URL = os.getenv("SPORTDB_BASE_URL", "https://www.thesportsdb.com/api/v1/json/3")

    # OpenAI / Ollama
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Modelos
    MODELS_PATH = os.getenv("MODELS_PATH", "C:\\Users\\Manuel Alejandro\\Downloads\\Mike\\models")

    # Ligas
    LEAGUES = [
        {"id": "4328", "name": "English Premier League", "country": "England", "priority": "high"},
        {"id": "4335", "name": "Spanish La Liga", "country": "Spain", "priority": "high"},
        {"id": "4332", "name": "German Bundesliga", "country": "Germany", "priority": "high"},
        {"id": "4331", "name": "Italian Serie A", "country": "Italy", "priority": "high"},
        {"id": "4334", "name": "French Ligue 1", "country": "France", "priority": "high"},
        {"id": "4344", "name": "Dutch Eredivisie", "country": "Netherlands", "priority": "medium"},
        {"id": "4340", "name": "Portuguese Primeira Liga", "country": "Portugal", "priority": "medium"},
        {"id": "4370", "name": "Brazilian Serie A", "country": "Brazil", "priority": "medium"},
        {"id": "4480", "name": "UEFA Champions League", "country": "Europe", "priority": "high"},
        {"id": "4481", "name": "UEFA Europa League", "country": "Europe", "priority": "medium"},
        {"id": "4482", "name": "UEFA Conference League", "country": "Europe", "priority": "low"},
        {"id": "4336", "name": "English Championship", "country": "England", "priority": "medium"},
    ]

    SEASONS = ["2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"]

settings = Settings()