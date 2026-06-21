from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class SimStateInfo(BaseModel):
    current_day: int
    is_running: bool
    last_run_at: Optional[datetime] = None
    total_orders_placed: int
    total_revenue: float

    class Config:
        from_attributes = True


class SimDayResult(BaseModel):
    day: int
    orders_created: int
    events_triggered: List[str]
    revenue_generated: float
    message: str


class MacroEventInfo(BaseModel):
    id: int
    name: str
    description: str
    category_path: str
    effect_type: str
    effect_value: float

    class Config:
        from_attributes = True


class HotRankingInfo(BaseModel):
    rank: int
    product_id: int
    product_title: str
    value: float


class MarketOverview(BaseModel):
    current_day: int
    top_sales: List[HotRankingInfo] = []
    top_gain: List[HotRankingInfo] = []
    top_loss: List[HotRankingInfo] = []
    events: List[dict] = []


class DecisionExplain(BaseModel):
    buyer_id: int
    buyer_tags: dict
    features: dict
    predicted_prob: float
    threshold: float
    decision: str
    decision_reason: str
    sim_day: int
    product_title: str = ""
    category_path: str = ""
