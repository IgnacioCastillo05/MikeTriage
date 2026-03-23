from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class SelectionOdds(BaseModel):
    selection_id: str
    selection_name: str
    new_odds: float
    probability: float
    adjustment_factor: float

class MarketOdds(BaseModel):
    market_id: str
    market_name: str
    market_type: str
    selections: List[SelectionOdds]

class OddsResponse(BaseModel):
    event_id: str
    calculated_at: datetime
    markets: List[MarketOdds]