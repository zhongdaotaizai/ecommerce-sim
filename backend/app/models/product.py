from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    image = Column(String(500), default="")
    base_price = Column(Float, nullable=False)
    total_sales = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    sentiment_score = Column(Float, default=0.0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    shop = relationship("Shop", back_populates="products")
    category = relationship("Category", back_populates="products")
    skus = relationship("SKU", back_populates="product", passive_deletes=True)

class SKU(Base):
    __tablename__ = "skus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    spec_json = Column(String(500), default="{}")
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    sales = Column(Integer, default=0)
    product = relationship("Product", back_populates="skus")
    cart_items = relationship("CartItem", back_populates="sku", passive_deletes=True)
    order_items = relationship("OrderItem", back_populates="sku", passive_deletes=True)

class PriceHistory(Base):
    __tablename__ = "price_histories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    record_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
