import kagglehub
import sqlite3
import pandas as pd
import logging
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "ecibethistorical")

def import_kaggle_data():
    logger.info("Iniciando importacion de Kaggle - SIN FILTRO DE LIGAS")

    try:
        path = kagglehub.dataset_download("hugomathien/soccer")
        logger.info(f"Dataset descargado en: {path}")

        db_path = os.path.join(path, "database.sqlite")
        conn = sqlite3.connect(db_path)

        matches_df = pd.read_sql_query("SELECT * FROM Match", conn)
        league_df = pd.read_sql_query("SELECT * FROM League", conn)
        team_df = pd.read_sql_query("SELECT * FROM Team", conn)

        conn.close()

        logger.info(f"Total partidos Kaggle: {len(matches_df)}")

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        db.historical_matches.create_index("externalId", unique=True)

        existing_ids = set(doc["externalId"] for doc in db.historical_matches.find({}, {"externalId": 1}))
        logger.info(f"Partidos existentes: {len(existing_ids)}")

        new_count = 0
        duplicate_count = 0
        error_count = 0

        for idx, match in matches_df.iterrows():
            try:
                league_id = match.get('league_id')
                league_row = league_df[league_df['id'] == league_id]
                if league_row.empty:
                    continue

                league_name = league_row.iloc[0]['name']

                home_team_id = match.get('home_team_api_id')
                away_team_id = match.get('away_team_api_id')

                home_team_row = team_df[team_df['team_api_id'] == home_team_id]
                away_team_row = team_df[team_df['team_api_id'] == away_team_id]

                if home_team_row.empty or away_team_row.empty:
                    continue

                home_team = home_team_row.iloc[0]['team_long_name']
                away_team = away_team_row.iloc[0]['team_long_name']

                home_goals = match.get('home_team_goal')
                away_goals = match.get('away_team_goal')

                if home_goals is None or away_goals is None:
                    continue

                season = match.get('season')
                if not season:
                    continue

                match_date = match.get('date')
                if match_date:
                    try:
                        match_date = datetime.strptime(match_date, "%Y-%m-%d %H:%M:%S")
                    except:
                        match_date = datetime.now()
                else:
                    match_date = datetime.now()

                external_id = f"kaggle_{match.get('id')}"

                if external_id in existing_ids:
                    duplicate_count += 1
                    continue

                match_doc = {
                    "externalId": external_id,
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeScore": int(home_goals),
                    "awayScore": int(away_goals),
                    "competition": league_name,
                    "competitionId": str(league_id),
                    "season": season,
                    "matchDate": match_date,
                    "status": "Match Finished",
                    "matchType": "MATCH",
                    "syncedAt": datetime.utcnow(),
                    "syncVersion": "kaggle_v1",
                    "syncStatus": "COMPLETED",
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }

                db.historical_matches.insert_one(match_doc)
                existing_ids.add(external_id)
                new_count += 1

                if new_count % 1000 == 0:
                    logger.info(f"Importados {new_count} partidos...")

            except Exception as e:
                error_count += 1
                if error_count <= 10:
                    logger.error(f"Error: {e}")
                continue

        client.close()

        logger.info(f"Importacion completada - Nuevos: {new_count}, Duplicados: {duplicate_count}, Errores: {error_count}")

        return {
            "status": "success",
            "new_matches": new_count,
            "duplicates": duplicate_count,
            "errors": error_count,
            "total_matches": len(existing_ids)
        }

    except Exception as e:
        logger.error(f"Error en importacion: {e}")
        return {"status": "error", "message": str(e)}

def import_all_kaggle_data():
    logger.info("Iniciando importacion completa de Kaggle (forzando todos los partidos)")

    try:
        path = kagglehub.dataset_download("hugomathien/soccer")
        logger.info(f"Dataset descargado en: {path}")

        db_path = os.path.join(path, "database.sqlite")
        conn = sqlite3.connect(db_path)

        matches_df = pd.read_sql_query("SELECT * FROM Match", conn)
        league_df = pd.read_sql_query("SELECT * FROM League", conn)
        team_df = pd.read_sql_query("SELECT * FROM Team", conn)

        conn.close()

        logger.info(f"Total partidos en Kaggle: {len(matches_df)}")

        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]

        db.historical_matches.create_index("externalId", unique=True)

        new_count = 0
        error_count = 0

        for idx, match in matches_df.iterrows():
            try:
                league_id = match.get('league_id')
                league_row = league_df[league_df['id'] == league_id]
                if league_row.empty:
                    continue

                league_name = league_row.iloc[0]['name']

                home_team_id = match.get('home_team_api_id')
                away_team_id = match.get('away_team_api_id')

                home_team_row = team_df[team_df['team_api_id'] == home_team_id]
                away_team_row = team_df[team_df['team_api_id'] == away_team_id]

                if home_team_row.empty or away_team_row.empty:
                    continue

                home_team = home_team_row.iloc[0]['team_long_name']
                away_team = away_team_row.iloc[0]['team_long_name']

                home_goals = match.get('home_team_goal')
                away_goals = match.get('away_team_goal')

                if home_goals is None or away_goals is None:
                    continue

                season = match.get('season')
                if not season:
                    continue

                match_date = match.get('date')
                if match_date:
                    try:
                        match_date = datetime.strptime(match_date, "%Y-%m-%d %H:%M:%S")
                    except:
                        match_date = datetime.now()
                else:
                    match_date = datetime.now()

                external_id = f"kaggle_{match.get('id')}"

                match_doc = {
                    "externalId": external_id,
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "homeScore": int(home_goals),
                    "awayScore": int(away_goals),
                    "competition": league_name,
                    "competitionId": str(league_id),
                    "season": season,
                    "matchDate": match_date,
                    "status": "Match Finished",
                    "matchType": "MATCH",
                    "syncedAt": datetime.utcnow(),
                    "syncVersion": "kaggle_v1",
                    "syncStatus": "COMPLETED",
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow()
                }

                db.historical_matches.update_one(
                    {"externalId": external_id},
                    {"$set": match_doc},
                    upsert=True
                )
                new_count += 1

                if new_count % 1000 == 0:
                    logger.info(f"Importados {new_count} partidos...")

            except Exception as e:
                error_count += 1
                if error_count <= 10:
                    logger.error(f"Error: {e}")
                continue

        client.close()

        logger.info(f"Importacion completada - Total: {new_count}, Errores: {error_count}")

        return {
            "status": "success",
            "total_matches": new_count,
            "errors": error_count
        }

    except Exception as e:
        logger.error(f"Error en importacion: {e}")
        return {"status": "error", "message": str(e)}

def get_kaggle_import_status():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    total = db.historical_matches.count_documents({})
    kaggle = db.historical_matches.count_documents({"syncVersion": "kaggle_v1"})
    sportdb = db.historical_matches.count_documents({"syncVersion": "sportdb_v1"})
    otros = total - kaggle - sportdb
    client.close()
    return {
        "total_matches": total,
        "kaggle_matches": kaggle,
        "sportdb_matches": sportdb,
        "otros": otros
    }