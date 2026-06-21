from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    image: Optional[str] = ""
    category_id: int


class SKUCreate(BaseModel):
    spec_json: str = "{}"
    price: float
    stock: int = 0


class SKUInfo(BaseModel):
    id: int
    product_id: int
    spec_json: str
    price: float
    stock: int
    sales: int

    class Config:
        from_attributes = True


class ProductInfo(BaseModel):
    id: int
    shop_id: int
    category_id: int
    title: str
    description: str
    image: str
    base_price: float
    total_sales: int
    avg_rating: float
    review_count: int
    is_active: int
    created_at: datetime
    skus: List[SKUInfo] = []

    class Config:
        from_attributes = True


class ProductListItem(BaseModel):
    id: int
    title: str
    image: str
    base_price: float
    total_sales: int
    avg_rating: float
    shop_name: Optional[str] = ""

    class Config:
        from_attributes = True


class PricePoint(BaseModel):
    date: str
    price: float


class ProductSearch(BaseModel):
    keyword: Optional[str] = ""
    category_id: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    page: int = 1
    page_size: int = 20
