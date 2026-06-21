from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.product import SKU, Product
from app.models.order import CartItem
from app.schemas.order import CartAdd, CartItemInfo
router = APIRouter()
@router.get("", response_model=List[CartItemInfo])
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    result = []
    for item in items:
        sku = db.query(SKU).options(joinedload(SKU.product)).filter(SKU.id == item.sku_id).first()
        if not sku:
            continue
        result.append(CartItemInfo(id=item.id, sku_id=item.sku_id, quantity=item.quantity, product_title=sku.product.title, spec_desc=sku.spec_json, price=sku.price, image=sku.product.image, stock=sku.stock))
    return result
@router.post("")
def add_to_cart(data: CartAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sku = db.query(SKU).filter(SKU.id == data.sku_id).first()
    if not sku:
        raise HTTPException(404, "SKU not found")
    existing = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.sku_id == data.sku_id).first()
    if existing:
        existing.quantity += data.quantity
    else:
        item = CartItem(user_id=current_user.id, sku_id=data.sku_id, quantity=data.quantity)
        db.add(item)
    db.commit()
    return {"message": "Added to cart"}
@router.delete("/{item_id}")
def remove_cart_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(404, "Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Removed from cart"}
@router.put("/{item_id}/quantity")
def update_cart_quantity(item_id: int, quantity: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(404, "Cart item not found")
    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity
    db.commit()
    return {"message": "Updated"}
