from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CartAdd(BaseModel):
    sku_id: int
    quantity: int = 1


class CartItemInfo(BaseModel):
    id: int
    sku_id: int
    quantity: int
    product_title: str = ""
    spec_desc: str = ""
    price: float = 0.0
    image: str = ""
    stock: int = 0

    class Config:
        from_attributes = True


class Checkout(BaseModel):
    cart_item_ids: List[int]


class OrderItemInfo(BaseModel):
    id: int
    sku_id: int
    product_title: str
    spec_desc: str
    price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True


class OrderInfo(BaseModel):
    id: int
    order_no: str
    total_amount: float
    status: str
    pay_fail_reason: str
    created_at: datetime
    paid_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    items: List[OrderItemInfo] = []

    class Config:
        from_attributes = True


class RefundApply(BaseModel):
    order_id: int
    type: str  # refund_only, return_refund
    reason: str


class RefundInfo(BaseModel):
    id: int
    order_id: int
    type: str
    reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    order_id: int
    sku_id: int
    rating: int
    content: Optional[str] = ""


class ReviewInfo(BaseModel):
    id: int
    order_id: int
    sku_id: int
    buyer_id: int
    rating: int
    content: str
    sentiment: float
    created_at: datetime

    class Config:
        from_attributes = True
