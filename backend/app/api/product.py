from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Shop
from app.models.category import Category
from app.models.product import Product, SKU, PriceHistory
from app.schemas.product import ProductCreate, SKUCreate, ProductInfo, SKUInfo, ProductListItem, PricePoint
router = APIRouter()

@router.get("/categories", response_model=List[dict])
def get_categories(level: Optional[int] = None, parent_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Category)
    if level is not None:
        q = q.filter(Category.level == level)
    if parent_id is not None:
        q = q.filter(Category.parent_id == parent_id)
    return [{"id": c.id, "name": c.name, "level": c.level, "parent_id": c.parent_id, "path": c.path, "min_price": c.min_price} for c in q.all()]

@router.get("", response_model=dict)
def search_products(keyword: Optional[str] = Query(""), category_id: Optional[int] = None, price_min: Optional[float] = None, price_max: Optional[float] = None, sort_by: Optional[str] = "default", page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    q = db.query(Product).filter(Product.is_active == 1)
    if keyword:
        q = q.filter(Product.title.like(f"%{keyword}%"))
    if category_id:
        sub_ids = [c.id for c in db.query(Category).filter(Category.path.like(db.query(Category.path).filter(Category.id == category_id).scalar() + "%")).all()]
        q = q.filter(Product.category_id.in_(sub_ids))
    if price_min is not None:
        q = q.filter(Product.base_price >= price_min)
    if price_max is not None:
        q = q.filter(Product.base_price <= price_max)
    total = q.count()
    if sort_by == "sales":
        q = q.order_by(desc(Product.total_sales))
    elif sort_by == "price_asc":
        q = q.order_by(Product.base_price)
    elif sort_by == "price_desc":
        q = q.order_by(desc(Product.base_price))
    elif sort_by == "rating":
        q = q.order_by(desc(Product.avg_rating))
    else:
        q = q.order_by(desc(Product.total_sales * 0.7 + func.coalesce(Product.avg_rating, 0) * 0.3))
    products = q.offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for p in products:
        shop = db.query(Shop).filter(Shop.id == p.shop_id).first()
        items.append(ProductListItem(id=p.id, title=p.title, image=p.image, base_price=p.base_price, total_sales=p.total_sales, avg_rating=p.avg_rating, shop_name=shop.name if shop else ""))
    return {"items": items, "total": total, "page": page, "page_size": page_size}

@router.get("/{product_id}", response_model=ProductInfo)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).options(joinedload(Product.skus)).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    return ProductInfo.model_validate(product)

@router.get("/{product_id}/price-history", response_model=List[PricePoint])
def get_price_history(product_id: int, sku_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(PriceHistory).join(SKU).filter(SKU.product_id == product_id)
    if sku_id:
        q = q.filter(PriceHistory.sku_id == sku_id)
    records = q.order_by(PriceHistory.record_date).all()
    return [PricePoint(date=r.record_date.strftime("%Y-%m-%d"), price=r.price) for r in records]

@router.post("", response_model=ProductInfo)
def create_product(data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(400, "Open a shop first")
    cat = db.query(Category).filter(Category.id == data.category_id, Category.level == 3).first()
    if not cat:
        raise HTTPException(400, "Must select a level-3 category")
    product = Product(shop_id=shop.id, category_id=data.category_id, title=data.title, description=data.description, image=data.image, base_price=0)
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductInfo.model_validate(product)

@router.post("/{product_id}/skus", response_model=SKUInfo)
def add_sku(product_id: int, data: SKUCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")
    shop = db.query(Shop).filter(Shop.id == product.shop_id).first()
    if shop.owner_id != current_user.id:
        raise HTTPException(403, "Not your product")
    cat = db.query(Category).filter(Category.id == product.category_id).first()
    if cat and cat.min_price > 0 and data.price < cat.min_price:
        raise HTTPException(400, f"Price cannot be lower than class base price {cat.min_price}")
    sku = SKU(product_id=product_id, spec_json=data.spec_json, price=data.price, stock=data.stock)
    db.add(sku)
    if product.base_price == 0 or data.price < product.base_price:
        product.base_price = data.price
    db.commit()
    db.refresh(sku)
    return SKUInfo.model_validate(sku)

@router.get("/seller/products", response_model=List[ProductInfo])
def get_my_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        return []
    products = db.query(Product).options(joinedload(Product.skus)).filter(Product.shop_id == shop.id).all()
    return [ProductInfo.model_validate(p) for p in products]
