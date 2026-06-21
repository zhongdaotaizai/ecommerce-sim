import threading
import time
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from typing import List
import random
import numpy as np
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User, Shop
from app.models.category import Category
from app.models.product import Product, SKU, PriceHistory
from app.models.order import Order, OrderItem, Review, Refund
from app.models.event import SimState, DailyEvent, HotRanking, DecisionLog
from app.ml.features import build_training_dataset, build_prediction_features_for_user, generate_virtual_review
from app.ml.model import PurchasePredictor
from app.tasks.event_pool import sample_events, get_event_price_modifier

def _get_or_create_state(db: Session) -> SimState:
    state = db.query(SimState).first()
    if not state:
        state = SimState(current_day=0)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state

def _create_hot_ranking(db: Session, day: int, rank_type: str, products: list, value_key: str):
    db.query(HotRanking).filter(HotRanking.sim_day == day, HotRanking.rank_type == rank_type).delete()
    sorted_products = sorted(products, key=lambda p: getattr(p, value_key, 0), reverse=(rank_type != "top_loss"))
    if rank_type == "top_loss":
        sorted_products = sorted(products, key=lambda p: getattr(p, value_key, 0))
    for rank, p in enumerate(sorted_products[:10], 1):
        value = float(getattr(p, value_key, 0))
        db.add(HotRanking(sim_day=day, rank_type=rank_type, product_id=p.id, product_title=p.title, value=value, rank=rank))

def _generate_virtual_buyer_preferences() -> dict:
    buyer_types = ["price_sensitive", "quality_oriented", "trend_follower", "impulse_buyer", "balanced"]
    btype = random.choice(buyer_types)
    if btype == "price_sensitive":
        return {"type": btype, "price_weight": round(random.uniform(0.7, 1.0), 2), "quality_weight": round(random.uniform(0.0, 0.3), 2), "trend_weight": round(random.uniform(0.0, 0.2), 2), "category_preference": ""}
    elif btype == "quality_oriented":
        return {"type": btype, "price_weight": round(random.uniform(0.0, 0.2), 2), "quality_weight": round(random.uniform(0.7, 1.0), 2), "trend_weight": round(random.uniform(0.0, 0.2), 2), "category_preference": ""}
    elif btype == "trend_follower":
        return {"type": btype, "price_weight": round(random.uniform(0.2, 0.4), 2), "quality_weight": round(random.uniform(0.2, 0.4), 2), "trend_weight": round(random.uniform(0.6, 1.0), 2), "category_preference": ""}
    elif btype == "impulse_buyer":
        return {"type": btype, "price_weight": round(random.uniform(0.3, 0.5), 2), "quality_weight": round(random.uniform(0.1, 0.3), 2), "trend_weight": round(random.uniform(0.3, 0.5), 2), "category_preference": ""}
    else:
        return {"type": btype, "price_weight": round(random.uniform(0.3, 0.6), 2), "quality_weight": round(random.uniform(0.3, 0.6), 2), "trend_weight": round(random.uniform(0.2, 0.4), 2), "category_preference": ""}

def _initialize_system_data(db: Session) -> dict:
    existing = db.query(User).filter(User.is_virtual.is_(True)).count()
    if existing > 0:
        return {"message": f"System already initialized with {existing} virtual users"}
    root_cats = [
        {"name": "Electronics", "level": 1, "children": [
            {"name": "Phones", "level": 2, "children": [{"name": "Smartphones", "level": 3, "min_price": 500}, {"name": "Accessories", "level": 3, "min_price": 10}]},
            {"name": "Computers", "level": 2, "children": [{"name": "Laptops", "level": 3, "min_price": 2000}, {"name": "Tablets", "level": 3, "min_price": 800}]}]},
        {"name": "Clothing", "level": 1, "children": [
            {"name": "Women", "level": 2, "children": [{"name": "Dresses", "level": 3, "min_price": 50}, {"name": "Tops", "level": 3, "min_price": 30}]},
            {"name": "Men", "level": 2, "children": [{"name": "Shirts", "level": 3, "min_price": 40}, {"name": "Pants", "level": 3, "min_price": 60}]}]},
        {"name": "Home", "level": 1, "children": [
            {"name": "Furniture", "level": 2, "children": [{"name": "Chairs", "level": 3, "min_price": 100}, {"name": "Tables", "level": 3, "min_price": 150}]},
            {"name": "Kitchen", "level": 2, "children": [{"name": "Cookware", "level": 3, "min_price": 20}, {"name": "Appliances", "level": 3, "min_price": 200}]}]},
        {"name": "Beauty", "level": 1, "children": [
            {"name": "Skincare", "level": 2, "children": [{"name": "Moisturizers", "level": 3, "min_price": 30}, {"name": "Serums", "level": 3, "min_price": 80}]},
            {"name": "Makeup", "level": 2, "children": [{"name": "Lipstick", "level": 3, "min_price": 15}, {"name": "Foundation", "level": 3, "min_price": 40}]}]},
        {"name": "Books", "level": 1, "children": [
            {"name": "Fiction", "level": 2, "children": [{"name": "Novels", "level": 3, "min_price": 10}, {"name": "Sci-Fi", "level": 3, "min_price": 12}]},
            {"name": "Education", "level": 2, "children": [{"name": "Textbooks", "level": 3, "min_price": 30}, {"name": "Reference", "level": 3, "min_price": 25}]}]},
    ]
    for rc in root_cats:
        rcat = Category(name=rc["name"], level=1, path=rc["name"])
        db.add(rcat)
        db.flush()
        for cc in rc.get("children", []):
            ccat = Category(name=cc["name"], level=2, parent_id=rcat.id, path=f"{rc['name']}/{cc['name']}")
            db.add(ccat)
            db.flush()
            for sc in cc.get("children", []):
                scat = Category(name=sc["name"], level=3, parent_id=ccat.id, path=f"{rc['name']}/{cc['name']}/{sc['name']}", min_price=sc.get("min_price", 0))
                db.add(scat)
    db.commit()
    categories = db.query(Category).filter(Category.level == 3).all()
    shop_names = ["TechZone", "FashionHub", "HomeDecor", "BeautyGlam", "BookWorm", "GadgetPro", "StyleVault", "GreenLiving", "EliteWear", "SmartBuy", "TrendSetter", "QualityFirst", "PriceBuster", "LuxuryLine", "DailyNeeds", "PetLover", "FitLife", "GourmetDelights", "BabyCare", "AutoParts"]
    product_templates = [
        "Premium {} - Top Quality", "Classic {} - Best Seller", "Deluxe {} - Limited Edition",
        "Essential {} - Daily Use", "Pro {} - Professional Grade", "Eco {} - Sustainable Choice",
        "Smart {} - AI Powered", "Vintage {} - Retro Style", "Modern {} - Latest Design",
        "Ultra {} - Performance Plus"
    ]
    cat_names = [c.name for c in categories]
    for i, sname in enumerate(shop_names):
        vuser = User(username=f"vshop_{i}", hashed_password="virtual", nickname=sname, is_virtual=True, is_seller=True, balance=50000, preferences={"type": "virtual_seller", "shop_name": sname})
        db.add(vuser)
        db.flush()
        shop = Shop(owner_id=vuser.id, name=sname, description=f"Virtual shop: {sname}", is_virtual=True)
        db.add(shop)
        db.flush()
        for j in range(random.randint(5, 8)):
            cat = random.choice(categories)
            tpl = random.choice(product_templates)
            title = tpl.format(random.choice(cat_names))
            price = cat.min_price + random.uniform(10, 500) if cat.min_price > 0 else random.uniform(20, 300)
            product = Product(shop_id=shop.id, category_id=cat.id, title=title, description=f"High quality {title.lower()}", image="", base_price=round(price, 2), total_sales=random.randint(0, 200), avg_rating=random.uniform(2.5, 5.0), review_count=random.randint(0, 30), is_active=1)
            db.add(product)
            db.flush()
            db.add(SKU(product_id=product.id, spec_json='{"default":"standard"}', price=round(price, 2), stock=random.randint(50, 500), sales=product.total_sales))
    db.commit()
    for i in range(settings.VIRTUAL_BUYER_COUNT):
        pref = _generate_virtual_buyer_preferences()
        pref["category_preference"] = random.choice(cat_names) if random.random() > 0.5 else ""
        db.add(User(username=f"vbuyer_{i}", hashed_password="virtual", nickname=f"Buyer_{i}", is_virtual=True, is_seller=False, balance=random.uniform(5000, 50000), preferences=pref))
    db.commit()
    state = _get_or_create_state(db)
    state.current_day = 0
    db.commit()
    return {"message": f"System initialized: {len(shop_names)} shops, {settings.VIRTUAL_BUYER_COUNT} virtual buyers"}

def _run_simulation_day(db: Session) -> dict:
    state = _get_or_create_state(db)
    state.is_running = 1
    db.commit()
    next_day = state.current_day + 1
    sampled_events = sample_events(settings.EVENT_COUNT_MIN, settings.EVENT_COUNT_MAX)
    for evt in sampled_events:
        db.add(DailyEvent(name=evt["name"], description=evt["description"], category_path=evt["category_path"], effect_type=evt["effect_type"], effect_value=evt["effect_value"], sim_day=next_day))
    db.commit()
    for shop in db.query(Shop).filter(Shop.is_virtual.is_(True)).all():
        for product in db.query(Product).filter(Product.shop_id == shop.id).all():
            for sku in db.query(SKU).filter(SKU.product_id == product.id).all():
                if sku.stock > 0 and sku.sales > 0:
                    sale_ratio = sku.sales / (sku.sales + sku.stock)
                    price_mod = get_event_price_modifier(sampled_events[0]) if sampled_events else 1.0
                    if sale_ratio > settings.PRICE_UP_THRESHOLD:
                        sku.price = round(sku.price * (1 + settings.PRICE_UP_RATE) * price_mod, 2)
                    elif sale_ratio < settings.PRICE_DOWN_THRESHOLD:
                        sku.price = round(sku.price * (1 - settings.PRICE_DOWN_RATE) * price_mod, 2)
                cat = db.query(Category).filter(Category.id == product.category_id).first()
                if cat and cat.min_price > 0 and sku.price < cat.min_price:
                    sku.price = cat.min_price
    db.commit()
    all_skus = db.query(SKU).all()
    for sku in all_skus:
        db.add(PriceHistory(sku_id=sku.id, price=sku.price, record_date=datetime.now(timezone.utc)))
    db.commit()
    df, feature_cols, _ = build_training_dataset(db, next_day)
    predictor = PurchasePredictor()
    if not df.empty and len(df) >= 10:
        df["purchased"] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])
        predictor.train(df, feature_cols, "purchased")
        predictor.save()
    virtual_buyers = db.query(User).filter(User.is_virtual.is_(True), User.is_seller.is_(False)).all()
    events_today = db.query(DailyEvent).filter(DailyEvent.sim_day == next_day).all()
    total_orders = 0
    total_revenue = 0.0
    for buyer in virtual_buyers:
        if random.random() > 0.4:
            continue
        purchases = random.randint(0, settings.MAX_ITEMS_PER_BUYER_PER_DAY)
        if purchases == 0:
            continue
        candidate_skus = random.sample(all_skus, min(20, len(all_skus)))
        items_bought = 0
        for sku in candidate_skus:
            if items_bought >= purchases:
                break
            if sku.stock <= 0:
                continue
            product = db.query(Product).filter(Product.id == sku.product_id).first()
            if not product or not product.is_active:
                continue
            features = build_prediction_features_for_user(db, buyer, product, sku, next_day, events_today)
            prob = predictor.predict_proba(features)
            for evt in events_today:
                cat = db.query(Category).filter(Category.id == product.category_id).first()
                if cat and evt.category_path and cat.path and cat.path.startswith(evt.category_path):
                    if evt.effect_type in ("demand_up", "promotion"):
                        prob = min(1.0, prob * (1 + evt.effect_value))
                    elif evt.effect_type == "demand_down":
                        prob = prob * (1 - evt.effect_value)
            if prob >= settings.PURCHASE_PROB_THRESHOLD:
                qty = 1
                if random.random() > 0.7:
                    qty = random.randint(1, 3)
                sku.stock -= qty
                subtotal = sku.price * qty
                order = Order(buyer_id=buyer.id, order_no=f"VS{next_day}{buyer.id}{random.randint(1000,9999)}", total_amount=subtotal, status="paid", paid_at=datetime.now(timezone.utc), received_at=datetime.now(timezone.utc) + timedelta(days=settings.AUTO_RECEIVE_DAYS))
                db.add(order)
                db.flush()
                db.add(OrderItem(order_id=order.id, sku_id=sku.id, product_title=product.title, spec_desc=sku.spec_json, price=sku.price, quantity=qty, subtotal=subtotal))
                sku.sales += qty
                product.total_sales += qty
                total_orders += 1
                total_revenue += subtotal
                items_bought += 1
                decision_reason = f"Probability {prob:.2f} >= threshold {settings.PURCHASE_PROB_THRESHOLD}, stock sufficient, purchased {qty} item(s)"
                db.add(DecisionLog(buyer_id=buyer.id, sku_id=sku.id, sim_day=next_day, features=features, predicted_prob=round(prob, 4), threshold=settings.PURCHASE_PROB_THRESHOLD, decision="buy", decision_reason=decision_reason))
                if random.random() > 0.5:
                    rating = random.choices([5, 4, 3, 2, 1], weights=[0.3, 0.35, 0.2, 0.1, 0.05])[0]
                    sentiment = (rating - 3) / 2.0
                    db.add(Review(order_id=order.id, sku_id=sku.id, buyer_id=buyer.id, rating=rating, content=generate_virtual_review(rating), sentiment=sentiment))
                    if product:
                        old_total = product.avg_rating * product.review_count
                        product.review_count += 1
                        product.avg_rating = (old_total + rating) / product.review_count
    db.commit()
    for rf in db.query(Refund).join(Order).filter(Refund.status == "pending").all():
        if random.random() < settings.VIRTUAL_REFUND_AGREE_RATE:
            rf.status = "agreed"
            order = db.query(Order).filter(Order.id == rf.order_id).first()
            if order:
                order.status = "refunded"
                for oi in order.items:
                    sku_item = db.query(SKU).filter(SKU.id == oi.sku_id).first()
                    if sku_item:
                        sku_item.stock += oi.quantity
        else:
            rf.status = "rejected"
        rf.resolved_at = datetime.now(timezone.utc)
    for o in db.query(Order).filter(Order.status == "paid", Order.received_at <= datetime.now(timezone.utc)).all():
        o.status = "received"
    db.commit()
    _create_hot_ranking(db, next_day, "top_sales", db.query(Product).filter(Product.is_active == 1).all(), "total_sales")
    db.commit()
    state.current_day = next_day
    state.is_running = 0
    state.total_orders_placed += total_orders
    state.total_revenue += total_revenue
    state.last_run_at = datetime.now(timezone.utc)
    db.commit()
    return {"day": next_day, "orders_created": total_orders, "revenue_generated": round(total_revenue, 2), "events_triggered": [e["name"] for e in sampled_events], "message": f"Day {next_day} completed: {total_orders} orders, ${total_revenue:.2f} revenue"}

