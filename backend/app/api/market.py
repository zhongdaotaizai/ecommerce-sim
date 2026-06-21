from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from app.core.database import get_db
from app.models.event import SimState, DailyEvent, HotRanking, DecisionLog
from app.models.product import Product, SKU
from app.models.user import User
from app.schemas.market import SimStateInfo, MacroEventInfo, HotRankingInfo, MarketOverview, DecisionExplain
router = APIRouter()
@router.get("/state", response_model=SimStateInfo)
def get_sim_state(db: Session = Depends(get_db)):
    state = db.query(SimState).first()
    if not state:
        state = SimState(current_day=0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return SimStateInfo.model_validate(state)
@router.get("/overview", response_model=MarketOverview)
def get_market_overview(day: Optional[int] = None, db: Session = Depends(get_db)):
    state = db.query(SimState).first()
    current_day = day if day else (state.current_day if state else 0)
    overview = MarketOverview(current_day=current_day)
    for rank_type, attr in [("top_sales", "top_sales"), ("top_gain", "top_gain"), ("top_loss", "top_loss")]:
        rankings = db.query(HotRanking).filter(HotRanking.sim_day == current_day, HotRanking.rank_type == rank_type).order_by(HotRanking.rank).limit(10).all()
        setattr(overview, attr, [HotRankingInfo(rank=r.rank, product_id=r.product_id, product_title=r.product_title, value=r.value) for r in rankings])
    events = db.query(DailyEvent).filter(DailyEvent.sim_day == current_day).all()
    overview.events = [{"id": e.id, "name": e.name, "description": e.description, "category_path": e.category_path, "effect_type": e.effect_type, "effect_value": e.effect_value} for e in events]
    return overview
@router.get("/price-history/{product_id}")
def get_product_price_history(product_id: int, db: Session = Depends(get_db)):
    from app.models.product import PriceHistory
    skus = db.query(SKU).filter(SKU.product_id == product_id).all()
    sku_ids = [s.id for s in skus]
    records = db.query(PriceHistory).filter(PriceHistory.sku_id.in_(sku_ids)).order_by(PriceHistory.record_date).all()
    return [{"date": r.record_date.strftime("%Y-%m-%d"), "price": r.price, "sku_id": r.sku_id} for r in records]
@router.get("/decision-log/{buyer_id}", response_model=List[DecisionExplain])
def get_decision_logs(buyer_id: int, limit: int = 10, db: Session = Depends(get_db)):
    logs = db.query(DecisionLog).filter(DecisionLog.buyer_id == buyer_id).order_by(DecisionLog.sim_day.desc()).limit(limit).all()
    results = []
    for log in logs:
        sku = db.query(SKU).filter(SKU.id == log.sku_id).first()
        product_title = ""
        if sku:
            product = db.query(Product).filter(Product.id == sku.product_id).first()
            product_title = product.title if product else ""
        buyer = db.query(User).filter(User.id == log.buyer_id).first()
        buyer_tags = buyer.preferences if buyer and buyer.preferences else {}
        categories = "N/A"
        results.append(DecisionExplain(
            buyer_id=log.buyer_id, buyer_tags=buyer_tags, features=log.features,
            predicted_prob=log.predicted_prob, threshold=log.threshold,
            decision=log.decision, decision_reason=log.decision_reason,
            sim_day=log.sim_day, product_title=product_title, category_path=categories
        ))
    return results
@router.get("/hot-rankings", response_model=List[HotRankingInfo])
def get_hot_rankings(rank_type: str = "top_sales", day: Optional[int] = None, db: Session = Depends(get_db)):
    state = db.query(SimState).first()
    current_day = day if day else (state.current_day if state else 0)
    rankings = db.query(HotRanking).filter(HotRanking.sim_day == current_day, HotRanking.rank_type == rank_type).order_by(HotRanking.rank).limit(10).all()
    return [HotRankingInfo(rank=r.rank, product_id=r.product_id, product_title=r.product_title, value=r.value) for r in rankings]
@router.get("/events", response_model=List[MacroEventInfo])
def get_macro_events(db: Session = Depends(get_db)):
    from app.models.event import MacroEvent
    events = db.query(MacroEvent).all()
    return [MacroEventInfo.model_validate(e) for e in events]
@router.get("/users/virtual")
def get_virtual_users(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_virtual == True).all()
    return [{"id": u.id, "username": u.username, "nickname": u.nickname, "preferences": u.preferences, "balance": u.balance} for u in users]
@router.get("/user/{user_id}/decision")
def get_user_decision_explain(user_id: int, db: Session = Depends(get_db)):
    log = db.query(DecisionLog).filter(DecisionLog.buyer_id == user_id).order_by(DecisionLog.sim_day.desc()).first()
    if not log:
        raise HTTPException(404, "No decision data found")
    sku = db.query(SKU).filter(SKU.id == log.sku_id).first()
    product_title = ""
    if sku:
        product = db.query(Product).filter(Product.id == sku.product_id).first()
        product_title = product.title if product else ""
    buyer = db.query(User).filter(User.id == user_id).first()
    buyer_tags = buyer.preferences if buyer and buyer.preferences else {}
    return DecisionExplain(buyer_id=user_id, buyer_tags=buyer_tags, features=log.features, predicted_prob=log.predicted_prob, threshold=log.threshold, decision=log.decision, decision_reason=log.decision_reason, sim_day=log.sim_day, product_title=product_title, category_path="")
@router.get("/decision-log/order/{order_id}")
def get_order_decision(order_id: int, db: Session = Depends(get_db)):
    from app.models.order import Order, OrderItem
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    decision_logs = db.query(DecisionLog).filter(DecisionLog.buyer_id == order.buyer_id).order_by(DecisionLog.sim_day.desc()).limit(5).all()
    return [DecisionExplain(
        buyer_id=dl.buyer_id, buyer_tags={}, features=dl.features,
        predicted_prob=dl.predicted_prob, threshold=dl.threshold,
        decision=dl.decision, decision_reason=dl.decision_reason,
        sim_day=dl.sim_day, product_title="", category_path=""
    ) for dl in decision_logs]
