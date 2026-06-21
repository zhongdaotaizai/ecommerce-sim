from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from datetime import datetime, timezone
from app.core.database import Base


class MacroEvent(Base):
    """Predefined macro event pool"""
    __tablename__ = "macro_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category_path = Column(String(200), default="")  # Affected category path prefix
    effect_type = Column(String(50), default="")  # price_up, price_down, demand_up, demand_down, promotion
    effect_value = Column(Float, default=0.0)  # Impact magnitude (e.g., 0.1 for 10%)
    probability = Column(Float, default=1.0)   # Relative probability of being selected


class DailyEvent(Base):
    """Events that occurred on a specific simulation day"""
    __tablename__ = "daily_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category_path = Column(String(200), default="")
    effect_type = Column(String(50), default="")
    effect_value = Column(Float, default=0.0)
    sim_day = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SimState(Base):
    """Track current simulation day and state"""
    __tablename__ = "sim_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    current_day = Column(Integer, default=0, nullable=False)
    is_running = Column(Integer, default=0)  # 0=idle, 1=running
    last_run_at = Column(DateTime, nullable=True)
    total_orders_placed = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class HotRanking(Base):
    """Daily hot rankings snapshot"""
    __tablename__ = "hot_rankings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sim_day = Column(Integer, nullable=False, index=True)
    rank_type = Column(String(20), nullable=False)  # top_sales, top_gain, top_loss
    product_id = Column(Integer, nullable=False)
    product_title = Column(String(500), default="")
    value = Column(Float, nullable=False)  # sales count or price change %
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DecisionLog(Base):
    """AI buyer decision log for explainability"""
    __tablename__ = "decision_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, nullable=False, index=True)
    sku_id = Column(Integer, nullable=False)
    sim_day = Column(Integer, nullable=False)
    features = Column(JSON, default=dict)     # Model input features snapshot
    predicted_prob = Column(Float, nullable=False)
    threshold = Column(Float, default=0.6)
    decision = Column(String(10), nullable=False)  # buy, skip
    decision_reason = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
