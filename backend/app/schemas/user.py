from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = ""
    email: Optional[str] = ""


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    email: str
    phone: str
    is_virtual: bool
    is_seller: bool
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class OpenShop(BaseModel):
    shop_name: str
    description: Optional[str] = ""


class ShopInfo(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str
    is_virtual: bool
    created_at: datetime

    class Config:
        from_attributes = True
