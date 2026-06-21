import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.models.product import Product, SKU, PriceHistory
from app.models.order import Order, OrderItem, Review
from app.models.user import User
from app.models.event import DailyEvent
from datetime import datetime, timezone, timedelta
def build_training_dataset(db: Session, current_day: int):
    """Build feature matrix from current system state for training the purchase prediction model."""
    rows = []
    products = db.query(Product).filter(Product.is_active == 1).all()
    for product in products:
        skus = db.query(SKU).filter(SKU.product_id == product.id).all()
        for sku in skus:
            reviews = db.query(Review).join(OrderItem, Review.sku_id == OrderItem.sku_id).filter(OrderItem.sku_id == sku.id).all()
            avg_rating = np.mean([r.rating for r in reviews]) if reviews else 3.0
            sentiment = np.mean([r.sentiment for r in reviews]) if reviews else 0.0
            review_count = len(reviews)
            row = {
                "product_id": product.id,
                "sku_id": sku.id,
                "category_id": product.category_id,
                "price": sku.price,
                "base_price": product.base_price,
                "historical_sales": sku.sales,
                "total_sales": product.total_sales,
                "avg_rating": avg_rating,
                "sentiment_score": sentiment,
                "review_count": review_count,
                "stock": sku.stock,
                "has_event_match": 0,
                "event_effect_value": 0.0,
            }
            rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df, [], []
    df["price_ratio"] = np.where(df["base_price"] > 0, df["price"] / df["base_price"], 1.0)
    df["stock_ratio"] = np.where(df["historical_sales"] + df["stock"] > 0, df["historical_sales"] / (df["historical_sales"] + df["stock"] + 1), 0.0)
    df["rating_norm"] = df["avg_rating"] / 5.0
    df["sales_rank"] = df["total_sales"].rank(pct=True)
    events = db.query(DailyEvent).filter(DailyEvent.sim_day == current_day).all()
    feature_cols = ["price", "historical_sales", "avg_rating", "sentiment_score", "review_count", "stock", "price_ratio", "stock_ratio", "rating_norm", "sales_rank", "has_event_match", "event_effect_value"]
    return df, feature_cols, events
def build_prediction_features_for_user(db: Session, user: User, product: Product, sku: SKU, current_day: int, events: list):
    """Build feature vector for a single user-product pair."""
    reviews = db.query(Review).join(OrderItem, Review.sku_id == OrderItem.sku_id).filter(OrderItem.sku_id == sku.id).all()
    avg_rating = np.mean([r.rating for r in reviews]) if reviews else 3.0
    sentiment = np.mean([r.sentiment for r in reviews]) if reviews else 0.0
    review_count = len(reviews)
    has_match = 0
    effect_val = 0.0
    for event in events:
        if event.category_path and product.category:
            if product.category.path and product.category.path.startswith(event.category_path):
                has_match = 1
                if event.effect_type == "demand_up":
                    effect_val = event.effect_value
                elif event.effect_type == "demand_down":
                    effect_val = -event.effect_value
    pref = user.preferences or {}
    price_weight = pref.get("price_weight", 0.5)
    quality_weight = pref.get("quality_weight", 0.3)
    features = {
        "price": sku.price,
        "historical_sales": sku.sales,
        "avg_rating": avg_rating,
        "sentiment_score": sentiment,
        "review_count": review_count,
        "stock": sku.stock,
        "price_ratio": sku.price / product.base_price if product.base_price > 0 else 1.0,
        "stock_ratio": sku.sales / (sku.sales + sku.stock + 1),
        "rating_norm": avg_rating / 5.0,
        "sales_rank": 0.5,
        "has_event_match": has_match,
        "event_effect_value": effect_val,
        "price_weight": price_weight,
        "quality_weight": quality_weight,
    }
    return features
def generate_virtual_review(rating: int) -> str:
    templates_pos = ["Great product, very satisfied!", "Good quality, fast delivery!", "Love it, would buy again!", "Exactly as described, happy!", "Worth the price, highly recommended!"]
    templates_neg = ["Not as expected, disappointed.", "Quality is poor, would not recommend.", "Took too long to arrive.", "Does not match description.", "Overpriced for what it is."]
    templates_mid = ["It's okay, nothing special.", "Average product, decent quality.", "Does the job, acceptable.", "Not bad but could be better.", "Fine for the price."]
    if rating >= 4:
        return np.random.choice(templates_pos)
    elif rating <= 2:
        return np.random.choice(templates_neg)
    else:
        return np.random.choice(templates_mid)
