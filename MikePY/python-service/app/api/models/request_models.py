from pydantic import BaseModel
from typing import Optional, Dict

class PreMatchRequest(BaseModel):
    event_id: str
    home_team: str
    away_team: str
    competition: Optional[str] = ""
    home_points_last5: Optional[float] = 7.5
    away_points_last5: Optional[float] = 7.5
    home_position: Optional[int] = 10
    away_position: Optional[int] = 10

class LiveUpdateRequest(BaseModel):
    event_id: str
    minute: int
    home_score: int
    away_score: int
    pre_match_features: Optional[Dict] = {}