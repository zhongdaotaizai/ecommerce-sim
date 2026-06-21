from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import os

_is_sqlite = settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    pool_size=20 if not _is_sqlite else 1,
    max_overflow=10 if not _is_sqlite else 0,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

redis_client = None
_redis_available = False
try:
    from redis import Redis
    redis_client = Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB,
        decode_responses=True, socket_connect_timeout=1,
    )
    redis_client.ping()
    _redis_available = True
    print("[Database] Redis connected")
except Exception:
    print("[Database] Redis not available, using in-memory fallback")
    redis_client = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    return redis_client

def create_tables():
    # Import all models to register them with Base.metadata
    from app.models.user import User, Shop
    from app.models.category import Category
    from app.models.product import Product, SKU, PriceHistory
    from app.models.order import CartItem, Order, OrderItem, Refund, Review
    from app.models.event import MacroEvent, DailyEvent, SimState, HotRanking, DecisionLog
    Base.metadata.create_all(bind=engine)
    print("[Database] Tables created/verified")
