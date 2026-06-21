from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class WalletTransactionInfo(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    balance_after: float
    order_id: Optional[int] = None
    description: str
    created_at: datetime
    class Config:
        from_attributes = True

class WalletInfo(BaseModel):
    balance: float
    total_income: float
    total_expense: float
    transactions: List[WalletTransactionInfo] = []
