from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.wallet import WalletTransaction
from app.schemas.wallet import WalletInfo, WalletTransactionInfo

router = APIRouter()

@router.get("/balance", response_model=WalletInfo)
def get_wallet(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    income = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.user_id == current_user.id,
        WalletTransaction.type == "income"
    ).scalar()
    expense = db.query(func.coalesce(func.sum(WalletTransaction.amount), 0)).filter(
        WalletTransaction.user_id == current_user.id,
        WalletTransaction.type == "expense"
    ).scalar()
    transactions = db.query(WalletTransaction).filter(
        WalletTransaction.user_id == current_user.id
    ).order_by(WalletTransaction.created_at.desc()).limit(20).all()
    return WalletInfo(
        balance=current_user.balance,
        total_income=float(income or 0),
        total_expense=float(expense or 0),
        transactions=[WalletTransactionInfo.model_validate(t) for t in transactions]
    )

@router.get("/transactions", response_model=List[WalletTransactionInfo])
def get_transactions(limit: int = 20, db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    txs = db.query(WalletTransaction).filter(
        WalletTransaction.user_id == current_user.id
    ).order_by(WalletTransaction.created_at.desc()).limit(limit).all()
    return [WalletTransactionInfo.model_validate(t) for t in txs]
