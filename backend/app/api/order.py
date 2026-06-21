from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timezone, timedelta
import random
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User, Shop
from app.models.product import Product, SKU
from app.models.order import Order, OrderItem, CartItem, Refund, Review
from app.schemas.order import Checkout, OrderInfo, RefundApply, RefundInfo, ReviewCreate, ReviewInfo
router = APIRouter()
def generate_order_no():
    return f"ORD{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{random.randint(1000,9999)}"
PAY_FAIL_REASONS = ["Insufficient balance", "Network timeout", "Risk control intercepted", "Bank declined", "Card expired"]
@router.post("/checkout", response_model=OrderInfo)
def checkout(data: Checkout, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.id.in_(data.cart_item_ids), CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(400, "No valid cart items")
    order = Order(buyer_id=current_user.id, order_no=generate_order_no(), total_amount=0.0, status="pending")
    db.add(order)
    db.flush()
    total = 0.0
    for ci in cart_items:
        sku = db.query(SKU).with_for_update().filter(SKU.id == ci.sku_id).first()
        if not sku or sku.stock < ci.quantity:
            db.rollback()
            raise HTTPException(400, f"Insufficient stock for SKU {ci.sku_id}")
        sku.stock -= ci.quantity
        subtotal = sku.price * ci.quantity
        total += subtotal
        product = db.query(Product).filter(Product.id == sku.product_id).first()
        oi = OrderItem(order_id=order.id, sku_id=sku.id, product_title=product.title if product else "", spec_desc=sku.spec_json, price=sku.price, quantity=ci.quantity, subtotal=subtotal)
        db.add(oi)
        db.delete(ci)
    order.total_amount = total
    db.commit()
    db.refresh(order)
    return OrderInfo.model_validate(order)
@router.post("/{order_id}/pay", response_model=OrderInfo)
def pay_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.buyer_id == current_user.id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    if order.status != "pending":
        raise HTTPException(400, "Order already paid or cancelled")
    success = random.random() < settings.PAYMENT_SUCCESS_RATE
    if success:
        order.status = "paid"
        order.paid_at = datetime.now(timezone.utc)
        # Auto receive after 3 days
        order.received_at = datetime.now(timezone.utc) + timedelta(days=settings.AUTO_RECEIVE_DAYS)
        current_user.balance -= order.total_amount
        # Add sales to skus
        for oi in order.items:
            sku = db.query(SKU).filter(SKU.id == oi.sku_id).first()
            if sku:
                sku.sales += oi.quantity
            product = db.query(Product).filter(Product.id == sku.product_id).first()
            if product:
                product.total_sales += oi.quantity
    else:
        order.status = "pending"
        order.pay_fail_reason = random.choice(PAY_FAIL_REASONS)
    db.commit()
    db.refresh(order)
    return OrderInfo.model_validate(order)
@router.get("", response_model=List[OrderInfo])
def list_orders(status: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Order).options(joinedload(Order.items)).filter(Order.buyer_id == current_user.id)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.created_at.desc()).all()
    return [OrderInfo.model_validate(o) for o in orders]
@router.post("/{order_id}/refund", response_model=RefundInfo)
def apply_refund(order_id: int, data: RefundApply, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.buyer_id == current_user.id).first()
    if not order or order.status not in ("paid", "received"):
        raise HTTPException(400, "Order cannot be refunded")
    refund = Refund(order_id=order.id, buyer_id=current_user.id, type=data.type, reason=data.reason, status="pending")
    db.add(refund)
    order.status = "refunding"
    db.commit()
    db.refresh(refund)
    return RefundInfo.model_validate(refund)
@router.post("/{order_id}/review", response_model=ReviewInfo)
def create_review(order_id: int, data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id, Order.buyer_id == current_user.id).first()
    if not order or order.status != "received":
        raise HTTPException(400, "Order not yet received")
    review = Review(order_id=order.id, sku_id=data.sku_id, buyer_id=current_user.id, rating=data.rating, content=data.content, sentiment=(data.rating - 3) / 2.0)
    db.add(review)
    # Update product rating
    product = db.query(Product).join(SKU).filter(SKU.id == data.sku_id).first()
    if product:
        old_total = product.avg_rating * product.review_count
        product.review_count += 1
        product.avg_rating = (old_total + data.rating) / product.review_count
    db.commit()
    db.refresh(review)
    return ReviewInfo.model_validate(review)
@router.get("/seller", response_model=List[OrderInfo])
def get_seller_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        return []
    products = db.query(Product).filter(Product.shop_id == shop.id).all()
    product_ids = [p.id for p in products]
    skus = db.query(SKU).filter(SKU.product_id.in_(product_ids)).all()
    sku_ids = [s.id for s in skus]
    orders = db.query(Order).options(joinedload(Order.items)).join(OrderItem).filter(OrderItem.sku_id.in_(sku_ids)).distinct().order_by(Order.created_at.desc()).all()
    return [OrderInfo.model_validate(o) for o in orders]
@router.post("/refund/{refund_id}/handle")
def handle_refund(refund_id: int, action: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(404, "Refund not found")
    if action == "agree":
        refund.status = "agreed"
        order = db.query(Order).filter(Order.id == refund.order_id).first()
        if order:
            order.status = "refunded"
            # Restore stock
            for oi in order.items:
                sku = db.query(SKU).filter(SKU.id == oi.sku_id).first()
                if sku:
                    sku.stock += oi.quantity
        refund.resolved_at = datetime.now(timezone.utc)
    elif action == "reject":
        refund.status = "rejected"
        order = db.query(Order).filter(Order.id == refund.order_id).first()
        if order:
            order.status = "received"
        refund.resolved_at = datetime.now(timezone.utc)
    else:
        raise HTTPException(400, "Invalid action")
    db.commit()
    return {"message": f"Refund {action}d"}

