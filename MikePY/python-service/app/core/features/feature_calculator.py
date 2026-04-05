import logging
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "ecibethistorical")

class FeatureCalculator:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.team_stats_cache = {}

    def calculate_team_stats(self, team_name, competition, season):
        cache_key = f"{team_name}_{competition}_{season}"
        if cache_key in self.team_stats_cache:
            return self.team_stats_cache[cache_key]

        matches = list(self.db.historical_matches.find({
            "$or": [
                {"homeTeam": team_name},
                {"awayTeam": team_name}
            ],
            "competition": competition,
            "season": season,
            "status": "Match Finished"
        }))

        if len(matches) < 5:
            return self._default_stats()

        total_points = 0
        total_goals_scored = 0
        total_goals_conceded = 0
        home_wins = 0
        home_draws = 0
        home_losses = 0
        away_wins = 0
        away_draws = 0
        away_losses = 0
        home_matches = 0
        away_matches = 0

        for match in matches:
            is_home = match.get("homeTeam") == team_name
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)

            if is_home:
                home_matches += 1
                total_goals_scored += home_score
                total_goals_conceded += away_score
                if home_score > away_score:
                    total_points += 3
                    home_wins += 1
                elif home_score < away_score:
                    home_losses += 1
                else:
                    total_points += 1
                    home_draws += 1
            else:
                away_matches += 1
                total_goals_scored += away_score
                total_goals_conceded += home_score
                if away_score > home_score:
                    total_points += 3
                    away_wins += 1
                elif away_score < home_score:
                    away_losses += 1
                else:
                    total_points += 1
                    away_draws += 1

        last_5_matches = matches[-5:] if len(matches) >= 5 else matches
        form = []
        for match in last_5_matches:
            is_home = match.get("homeTeam") == team_name
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)
            if is_home:
                if home_score > away_score:
                    form.append("W")
                elif home_score < away_score:
                    form.append("L")
                else:
                    form.append("D")
            else:
                if away_score > home_score:
                    form.append("W")
                elif away_score < home_score:
                    form.append("L")
                else:
                    form.append("D")

        form_str = "".join(form).ljust(5, "D")[:5]
        form_points = sum(3 if r == "W" else 1 if r == "D" else 0 for r in form_str)

        standing = self.db.standings.find_one({
            "teamName": team_name,
            "leagueName": competition,
            "season": season
        })

        position = standing.get("rank", 10) if standing else 10
        goals_avg = total_goals_scored / max(len(matches), 1)

        stats = {
            "position": position,
            "points_last5": form_points,
            "goals_avg": round(goals_avg, 2),
            "form": form_str,
            "total_points": total_points,
            "matches_played": len(matches)
        }

        self.team_stats_cache[cache_key] = stats
        return stats

    def _default_stats(self):
        return {
            "position": 10,
            "points_last5": 7,
            "goals_avg": 1.5,
            "form": "DDDDD",
            "total_points": 10,
            "matches_played": 0
        }

    def get_h2h_stats(self, home_team, away_team, competition):
        matches = list(self.db.historical_matches.find({
            "$or": [
                {"homeTeam": home_team, "awayTeam": away_team},
                {"homeTeam": away_team, "awayTeam": home_team}
            ],
            "competition": competition,
            "status": "Match Finished"
        }).sort("matchDate", -1).limit(10))

        if not matches:
            return {"home_wins": 0, "draws": 0, "away_wins": 0, "avg_goals": 0}

        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = 0

        for match in matches:
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)
            total_goals += home_score + away_score

            if match.get("homeTeam") == home_team:
                if home_score > away_score:
                    home_wins += 1
                elif home_score < away_score:
                    away_wins += 1
                else:
                    draws += 1
            else:
                if away_score > home_score:
                    home_wins += 1
                elif away_score < home_score:
                    away_wins += 1
                else:
                    draws += 1

        return {
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "avg_goals": round(total_goals / len(matches), 2)
        }

feature_calculator = FeatureCalculator()