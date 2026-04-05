import logging
import re
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "ecibethistorical")

class TeamStatsCalculator:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.cache = {}
        self.team_name_cache = {}

    def _normalize_name(self, name):
        name = name.lower()
        name = re.sub(r'[^a-z0-9]', '', name)
        return name

    def _find_team_in_db(self, team_name):
        cache_key = f"find_{team_name}"
        if cache_key in self.team_name_cache:
            return self.team_name_cache[cache_key]

        all_teams = list(self.db.historical_matches.aggregate([
            {"$match": {"syncVersion": "kaggle_v1"}},
            {"$group": {"_id": None, "teams": {"$addToSet": "$homeTeam"}}}
        ]))

        if not all_teams:
            self.team_name_cache[cache_key] = None
            return None

        teams = all_teams[0].get("teams", [])
        normalized_input = self._normalize_name(team_name)

        best_match = None
        best_score = 0

        for db_team in teams:
            normalized_db = self._normalize_name(db_team)

            if normalized_input == normalized_db:
                best_match = db_team
                break

            if normalized_input in normalized_db or normalized_db in normalized_input:
                score = len(normalized_input) + len(normalized_db)
                if score > best_score:
                    best_score = score
                    best_match = db_team

        self.team_name_cache[cache_key] = best_match

        if best_match:
            logger.info(f"Encontrado {team_name} -> {best_match}")
        else:
            logger.warning(f"No se encontro equipo similar a {team_name}")

        return best_match

    def get_team_stats(self, team_name, competition, season):
        cache_key = f"{team_name}_{competition}_{season}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        real_team_name = self._find_team_in_db(team_name)

        if not real_team_name:
            return self._default_stats(team_name)

        matches = list(self.db.historical_matches.find({
            "$or": [
                {"homeTeam": real_team_name},
                {"awayTeam": real_team_name}
            ],
            "season": season,
            "syncVersion": "kaggle_v1",
            "status": "Match Finished",
            "homeScore": {"$exists": True},
            "awayScore": {"$exists": True}
        }).sort("matchDate", -1))

        if len(matches) < 3:
            matches = list(self.db.historical_matches.find({
                "$or": [
                    {"homeTeam": real_team_name},
                    {"awayTeam": real_team_name}
                ],
                "syncVersion": "kaggle_v1",
                "status": "Match Finished",
                "homeScore": {"$exists": True},
                "awayScore": {"$exists": True}
            }).sort("matchDate", -1).limit(38))

            if len(matches) < 3:
                logger.warning(f"Pocos partidos para {real_team_name} ({team_name}): {len(matches)}")
                return self._default_stats(team_name)

            logger.warning(f"Usando datos de otras temporadas para {team_name} ({real_team_name})")

        total_points = 0
        total_goals_scored = 0
        total_goals_conceded = 0
        wins = 0
        draws = 0
        losses = 0

        for match in matches:
            is_home = match.get("homeTeam") == real_team_name
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)

            if is_home:
                total_goals_scored += home_score
                total_goals_conceded += away_score
                if home_score > away_score:
                    total_points += 3
                    wins += 1
                elif home_score < away_score:
                    losses += 1
                else:
                    total_points += 1
                    draws += 1
            else:
                total_goals_scored += away_score
                total_goals_conceded += home_score
                if away_score > home_score:
                    total_points += 3
                    wins += 1
                elif away_score < home_score:
                    losses += 1
                else:
                    total_points += 1
                    draws += 1

        last_5_matches = matches[:5]
        form = []
        form_points = 0
        for match in last_5_matches:
            is_home = match.get("homeTeam") == real_team_name
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)
            if is_home:
                if home_score > away_score:
                    form.append("W")
                    form_points += 3
                elif home_score < away_score:
                    form.append("L")
                else:
                    form.append("D")
                    form_points += 1
            else:
                if away_score > home_score:
                    form.append("W")
                    form_points += 3
                elif away_score < home_score:
                    form.append("L")
                else:
                    form.append("D")
                    form_points += 1

        form_str = "".join(form).ljust(5, "D")[:5]
        goals_avg = round(total_goals_scored / max(len(matches), 1), 2)

        position = self._calculate_position(real_team_name, matches)

        stats = {
            "team_name": team_name,
            "real_name": real_team_name,
            "position": position,
            "points_last5": form_points,
            "goals_avg": goals_avg,
            "form": form_str,
            "points": total_points,
            "matches_played": len(matches),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_scored": total_goals_scored,
            "goals_conceded": total_goals_conceded,
        }

        self.cache[cache_key] = stats
        logger.info(f"Estadisticas de {team_name} ({real_team_name}): pos={stats['position']}, pts_ult5={stats['points_last5']}, goles_avg={stats['goals_avg']}, forma={stats['form']}, partidos={stats['matches_played']}")
        return stats

    def get_h2h_stats(self, home_team, away_team, competition, season):
        cache_key = f"h2h_{home_team}_{away_team}_{competition}_{season}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        real_home = self._find_team_in_db(home_team)
        real_away = self._find_team_in_db(away_team)

        if not real_home or not real_away:
            return {"home_wins": 0, "draws": 0, "away_wins": 0, "avg_goals": 0, "matches_played": 0}

        matches = list(self.db.historical_matches.find({
            "$or": [
                {"homeTeam": real_home, "awayTeam": real_away},
                {"homeTeam": real_away, "awayTeam": real_home}
            ],
            "syncVersion": "kaggle_v1",
            "status": "Match Finished",
            "homeScore": {"$exists": True},
            "awayScore": {"$exists": True}
        }).sort("matchDate", -1).limit(10))

        if not matches:
            return {"home_wins": 0, "draws": 0, "away_wins": 0, "avg_goals": 0, "matches_played": 0}

        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = 0

        for match in matches:
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)
            total_goals += home_score + away_score

            if match.get("homeTeam") == real_home:
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

        stats = {
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "avg_goals": round(total_goals / len(matches), 2),
            "matches_played": len(matches)
        }

        self.cache[cache_key] = stats
        logger.info(f"H2H {home_team} vs {away_team}: {home_wins}-{draws}-{away_wins}")
        return stats

    def _calculate_position(self, team_name, matches):
        if not matches:
            return 20

        all_teams = {}
        for match in matches:
            home_team = match.get("homeTeam")
            away_team = match.get("awayTeam")
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)

            if home_team not in all_teams:
                all_teams[home_team] = 0
            if away_team not in all_teams:
                all_teams[away_team] = 0

            if home_score > away_score:
                all_teams[home_team] += 3
            elif home_score < away_score:
                all_teams[away_team] += 3
            else:
                all_teams[home_team] += 1
                all_teams[away_team] += 1

        sorted_teams = sorted(all_teams.items(), key=lambda x: x[1], reverse=True)

        for idx, (team, _) in enumerate(sorted_teams):
            if team == team_name:
                return idx + 1

        return len(sorted_teams) + 1

    def _default_stats(self, team_name):
        return {
            "team_name": team_name,
            "real_name": None,
            "position": 20,
            "points_last5": 5,
            "goals_avg": 1.2,
            "form": "DDDDD",
            "points": 0,
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_scored": 0,
            "goals_conceded": 0,
        }

team_stats_calculator = TeamStatsCalculator()