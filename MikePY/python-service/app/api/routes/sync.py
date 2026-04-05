from fastapi import APIRouter
import logging
import httpx
from datetime import datetime
from typing import Dict, Any
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

router = APIRouter()
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "ecibethistorical")
SPORTDB_API_KEY = os.getenv("SPORTDB_API_KEY", "3")
SPORTDB_BASE_URL = os.getenv("SPORTDB_BASE_URL", "https://www.thesportsdb.com/api/v1/json/3")

LEAGUES = [
    {"id": "4328", "name": "English Premier League"},
    {"id": "4335", "name": "Spanish La Liga"},
    {"id": "4332", "name": "German Bundesliga"},
    {"id": "4331", "name": "Italian Serie A"},
    {"id": "4334", "name": "French Ligue 1"},
]

SEASONS = ["2023-2024", "2024-2025"]

@router.post("/sync/all")
async def sync_all_leagues(years_back: int = 2):
    logger.info(f"Sincronizando {len(LEAGUES)} ligas")

    results = []
    for league in LEAGUES:
        for season in SEASONS[-years_back:]:
            try:
                result = await sync_league_season(league["id"], league["name"], season)
                results.append(result)
            except Exception as e:
                results.append({"league": league["name"], "season": season, "error": str(e)})

    return {"status": "completed", "results": results}

async def sync_league_season(league_id: str, league_name: str, season: str) -> Dict[str, Any]:
    logger.info(f"Sincronizando {league_name} - {season}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SPORTDB_BASE_URL}/{SPORTDB_API_KEY}/eventsseason.php",
            params={"id": league_id, "s": season}
        )

        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])

            if events:
                client_mongo = MongoClient(MONGO_URI)
                db = client_mongo[DB_NAME]

                for event in events:
                    event_doc = {
                        "externalId": event.get("idEvent"),
                        "homeTeam": event.get("strHomeTeam"),
                        "awayTeam": event.get("strAwayTeam"),
                        "homeScore": int(event.get("intHomeScore", 0)) if event.get("intHomeScore") else None,
                        "awayScore": int(event.get("intAwayScore", 0)) if event.get("intAwayScore") else None,
                        "competition": league_name,
                        "competitionId": league_id,
                        "season": season,
                        "status": event.get("strStatus", "Unknown"),
                        "matchType": "MATCH",
                        "syncedAt": datetime.utcnow(),
                        "syncVersion": "v2"
                    }

                    db.historical_matches.update_one(
                        {"externalId": event_doc["externalId"]},
                        {"$set": event_doc},
                        upsert=True
                    )

                client_mongo.close()
                return {"league": league_name, "season": season, "events_synced": len(events), "status": "success"}
            else:
                return {"league": league_name, "season": season, "events_synced": 0, "status": "no_events"}
        else:
            return {"league": league_name, "season": season, "status": "error", "code": response.status_code}

@router.get("/sync/status")
async def get_sync_status():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    total_matches = db.historical_matches.count_documents({})

    client.close()

    return {
        "total_matches": total_matches,
        "leagues_configured": len(LEAGUES)
    }