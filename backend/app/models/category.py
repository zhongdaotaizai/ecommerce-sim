from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), default=None, index=True)
    path = Column(String(500), default="")
    min_price = Column(Float, default=0.0)
    children = relationship("Category", backref="parent", remote_side=[id], passive_deletes=True)
    products = relationship("Product", back_populates="category", passive_deletes=True)
