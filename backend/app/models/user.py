from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(100), default="")
    avatar = Column(String(500), default="")
    email = Column(String(100), default="")
    phone = Column(String(20), default="")
    is_virtual = Column(Boolean, default=False, index=True)
    is_seller = Column(Boolean, default=False)
    balance = Column(Float, default=10000.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    preferences = Column(JSON, default=dict)
    shop = relationship("Shop", uselist=False, back_populates="owner", passive_deletes=True)
    cart_items = relationship("CartItem", back_populates="user", passive_deletes=True)
    orders = relationship("Order", back_populates="buyer", passive_deletes=True)

class Shop(Base):
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    is_virtual = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner = relationship("User", back_populates="shop", foreign_keys=[owner_id])
    products = relationship("Product", back_populates="shop", passive_deletes=True)
