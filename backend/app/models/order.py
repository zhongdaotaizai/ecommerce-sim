from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="cart_items")
    sku = relationship("SKU", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, shipped, received, refunding, refunded, cancelled
    pay_fail_reason = Column(String(100), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    paid_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)

    buyer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", passive_deletes=True)
    refunds = relationship("Refund", back_populates="order", passive_deletes=True)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    product_title = Column(String(500), default="")
    spec_desc = Column(String(200), default="")
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    sku = relationship("SKU", back_populates="order_items")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(20), nullable=False)  # refund_only, return_refund
    reason = Column(String(500), default="")
    status = Column(String(20), default="pending")  # pending, agreed, rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="refunds")
    buyer = relationship("User")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    content = Column(Text, default="")
    sentiment = Column(Float, default=0.0)  # positive/negative score
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order")
    sku = relationship("SKU")
    buyer = relationship("User")
