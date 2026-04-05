import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class TeamStatsCalculator:
    def __init__(self, mongodb_uri: str, db_name: str):
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[db_name]

    def get_team_stats(self, team_name: str, competition: str, season: str) -> Dict[str, Any]:
        matches = list(self.db.historical_matches.find({
            "$or": [
                {"homeTeam": team_name, "competition": competition, "season": season},
                {"awayTeam": team_name, "competition": competition, "season": season}
            ],
            "status": "Match Finished"
        }))

        if not matches:
            return self._default_stats()

        home_matches = [m for m in matches if m.get("homeTeam") == team_name]
        away_matches = [m for m in matches if m.get("awayTeam") == team_name]

        stats = {
            "position": self._get_league_position(team_name, competition, season),
            "points": self._calculate_points(matches, team_name),
            "form_last5": self._calculate_form(matches[-5:], team_name),
            "goals_scored_avg": self._calculate_avg_goals_scored(matches, team_name),
            "goals_conceded_avg": self._calculate_avg_goals_conceded(matches, team_name),
            "home_wins_pct": len([m for m in home_matches if m.get("homeScore", 0) > m.get("awayScore", 0)]) / max(len(home_matches), 1),
            "home_draws_pct": len([m for m in home_matches if m.get("homeScore", 0) == m.get("awayScore", 0)]) / max(len(home_matches), 1),
            "home_losses_pct": len([m for m in home_matches if m.get("homeScore", 0) < m.get("awayScore", 0)]) / max(len(home_matches), 1),
            "away_wins_pct": len([m for m in away_matches if m.get("awayScore", 0) > m.get("homeScore", 0)]) / max(len(away_matches), 1),
            "away_draws_pct": len([m for m in away_matches if m.get("awayScore", 0) == m.get("homeScore", 0)]) / max(len(away_matches), 1),
            "away_losses_pct": len([m for m in away_matches if m.get("awayScore", 0) < m.get("homeScore", 0)]) / max(len(away_matches), 1),
            "avg_possession": self._calculate_avg_possession(matches, team_name),
            "avg_shots": self._calculate_avg_shots(matches, team_name),
        }

        return stats

    def get_h2h_stats(self, home_team: str, away_team: str, competition: str) -> Dict[str, Any]:
        matches = list(self.db.historical_matches.find({
            "$or": [
                {"homeTeam": home_team, "awayTeam": away_team},
                {"homeTeam": away_team, "awayTeam": home_team}
            ],
            "competition": competition,
            "status": "Match Finished"
        }).sort("matchDate", -1).limit(10))

        if not matches:
            return {"home_wins": 0, "draws": 0, "away_wins": 0, "avg_goals": 0, "last_result": "N/A"}

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
            "avg_goals": total_goals / len(matches),
            "last_result": self._get_last_result(matches[0], home_team)
        }

    def _default_stats(self) -> Dict[str, Any]:
        return {
            "position": 10,
            "points": 10,
            "form_last5": "DDDDD",
            "goals_scored_avg": 1.5,
            "goals_conceded_avg": 1.5,
            "home_wins_pct": 0.33,
            "home_draws_pct": 0.34,
            "home_losses_pct": 0.33,
            "away_wins_pct": 0.33,
            "away_draws_pct": 0.34,
            "away_losses_pct": 0.33,
            "avg_possession": 50,
            "avg_shots": 10
        }

    def _calculate_points(self, matches: List[Dict], team_name: str) -> int:
        points = 0
        for match in matches:
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)

            if match.get("homeTeam") == team_name:
                if home_score > away_score:
                    points += 3
                elif home_score == away_score:
                    points += 1
            else:
                if away_score > home_score:
                    points += 3
                elif away_score == home_score:
                    points += 1
        return points

    def _calculate_form(self, matches: List[Dict], team_name: str) -> str:
        form = ""
        for match in matches:
            home_score = match.get("homeScore", 0)
            away_score = match.get("awayScore", 0)

            if match.get("homeTeam") == team_name:
                if home_score > away_score:
                    form += "W"
                elif home_score < away_score:
                    form += "L"
                else:
                    form += "D"
            else:
                if away_score > home_score:
                    form += "W"
                elif away_score < home_score:
                    form += "L"
                else:
                    form += "D"
        return form.ljust(5, "D")[:5]

    def _calculate_avg_goals_scored(self, matches: List[Dict], team_name: str) -> float:
        total = 0
        for match in matches:
            if match.get("homeTeam") == team_name:
                total += match.get("homeScore", 0)
            else:
                total += match.get("awayScore", 0)
        return total / max(len(matches), 1)

    def _calculate_avg_goals_conceded(self, matches: List[Dict], team_name: str) -> float:
        total = 0
        for match in matches:
            if match.get("homeTeam") == team_name:
                total += match.get("awayScore", 0)
            else:
                total += match.get("homeScore", 0)
        return total / max(len(matches), 1)

    def _calculate_avg_possession(self, matches: List[Dict], team_name: str) -> float:
        total = 0
        count = 0
        for match in matches:
            possession = match.get(f"{team_name.lower()}_possession")
            if possession:
                total += possession
                count += 1
        return total / max(count, 1)

    def _calculate_avg_shots(self, matches: List[Dict], team_name: str) -> float:
        total = 0
        count = 0
        for match in matches:
            shots = match.get(f"{team_name.lower()}_shots")
            if shots:
                total += shots
                count += 1
        return total / max(count, 1)

    def _get_league_position(self, team_name: str, competition: str, season: str) -> int:
        standing = self.db.standings.find_one({
            "teamName": team_name,
            "leagueId": competition,
            "season": season
        })
        return standing.get("rank", 10) if standing else 10

    def _get_last_result(self, match: Dict, home_team: str) -> str:
        home_score = match.get("homeScore", 0)
        away_score = match.get("awayScore", 0)

        if match.get("homeTeam") == home_team:
            if home_score > away_score:
                return "H"
            elif home_score < away_score:
                return "A"
            else:
                return "D"
        else:
            if away_score > home_score:
                return "H"
            elif away_score < home_score:
                return "A"
            else:
                return "D"