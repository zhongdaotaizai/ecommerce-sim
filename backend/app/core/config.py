from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "AI Ecommerce Sim"
    DEBUG: bool = True
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASS: str = "root"
    DB_NAME: str = "ecommerce_sim"
    DATABASE_URL: str = "sqlite:///./data/ecommerce.db"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    USE_CELERY: bool = False
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    VIRTUAL_BUYER_COUNT: int = 500
    PURCHASE_PROB_THRESHOLD: float = 0.6
    MAX_ITEMS_PER_BUYER_PER_DAY: int = 3
    PAYMENT_SUCCESS_RATE: float = 0.9
    AUTO_RECEIVE_DAYS: int = 3
    VIRTUAL_REFUND_AGREE_RATE: float = 0.8
    EVENT_COUNT_MIN: int = 1
    EVENT_COUNT_MAX: int = 3
    PRICE_UP_THRESHOLD: float = 0.5
    PRICE_DOWN_THRESHOLD: float = 0.1
    PRICE_UP_RATE: float = 0.05
    PRICE_DOWN_RATE: float = 0.03
    MODEL_PATH: str = "data/model.pkl"
    MODEL_FEATURES_PATH: str = "data/features.pkl"
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(root_dir, "data")
os.makedirs(data_dir, exist_ok=True)
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    db_path = os.path.join(data_dir, "ecommerce.db")
    settings.DATABASE_URL = f"sqlite:///{db_path}"
    print(f"[Config] Using SQLite: {db_path}")
