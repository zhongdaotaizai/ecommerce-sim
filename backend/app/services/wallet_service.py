from sqlalchemy.orm import Session
from app.models.user import User
from app.models.wallet import WalletTransaction
from datetime import datetime, timezone

def add_wallet_transaction(db: Session, user_id: int, tx_type: str, amount: float,
                           order_id=None, description=""):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if tx_type == "expense":
        user.balance -= amount
    elif tx_type == "income":
        user.balance += amount
    elif tx_type == "refund":
        user.balance += amount
    tx = WalletTransaction(
        user_id=user_id,
        type=tx_type,
        amount=round(amount, 2),
        balance_after=round(user.balance, 2),
        order_id=order_id,
        description=description,
        created_at=datetime.now(timezone.utc)
    )
    db.add(tx)
    db.flush()
    return tx
