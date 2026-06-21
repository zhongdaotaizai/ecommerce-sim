"""
load_dataset.py
Reads Kaggle RetailRocket or Brazilian E-Commerce dataset and maps to system tables.
Usage: python load_dataset.py --source retailrocket --data-path /path/to/data.csv
"""
import argparse
import csv
import random
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, Shop
from app.models.category import Category
from app.models.product import Product, SKU
from app.models.order import Order, OrderItem, Review
from app.models.event import SimState
from app.core.config import settings


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified.")


def load_retailrocket(path):
    """Load RetailRocket dataset (events.csv, items.csv, category_tree.csv)."""
    db = SessionLocal()
    try:
        dir_path = os.path.dirname(path) if os.path.isfile(path) else path
        events_file = os.path.join(dir_path, "events.csv")
        items_file = os.path.join(dir_path, "items.csv")
        cat_tree_file = os.path.join(dir_path, "category_tree.csv")
        print(f"Reading from {dir_path}")
        categories = {}
        if os.path.exists(cat_tree_file):
            with open(cat_tree_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cid = int(row["categoryid"])
                    pid = row.get("parentid")
                    categories[cid] = {"id": cid, "parent_id": int(pid) if pid else None}
            # Build SQL categories
            cat_objects = {}
            for cid, cat in categories.items():
                if cat["parent_id"] is None:
                    c = Category(name=f"Category_{cid}", level=1, path=f"Category_{cid}")
                else:
                    parent = cat_objects.get(cat["parent_id"])
                    if parent:
                        c = Category(name=f"Cat_{cid}", level=parent.level + 1, parent_id=parent.id, path=f"{parent.path}/Cat_{cid}", min_price=random.uniform(5, 50))
                    else:
                        c = Category(name=f"Category_{cid}", level=2, path=f"Category_{cid}", min_price=random.uniform(5, 50))
                db.add(c)
                db.flush()
                cat_objects[cid] = c
            db.commit()
            print(f"Created {len(cat_objects)} categories")
        items = {}
        if os.path.exists(items_file):
            with open(items_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    iid = int(row["itemid"])
                    cid = int(row.get("categoryid", 0)) if row.get("categoryid") else None
                    items[iid] = {"id": iid, "category_id": cid}
        # Create virtual shops and products
        shop_names_retail = ["TechStore", "FashionWorld", "HomeGoods", "BeautyPlus", "BookNook"]
        for i, sname in enumerate(shop_names_retail):
            vuser = User(username=f"rs_{sname.lower()}", hashed_password="virtual", nickname=sname, is_virtual=True, is_seller=True, balance=50000)
            db.add(vuser)
            db.flush()
            shop = Shop(owner_id=vuser.id, name=sname, description=f"Retail shop: {sname}", is_virtual=True)
            db.add(shop)
            db.flush()
            cat_ids = list(cat_objects.keys()) if cat_objects else range(1, 11)
            item_sample = random.sample(list(items.keys()), min(30, len(items))) if items else []
            for item_id in item_sample:
                cat = cat_objects.get(random.choice(cat_ids)) if cat_objects else None
                if not cat and cat_objects:
                    cat = random.choice(list(cat_objects.values()))
                elif not cat:
                    continue
                price = random.uniform(10, 500)
                product = Product(shop_id=shop.id, category_id=cat.id, title=f"Item_{item_id}", description=f"Product from RetailRocket dataset", image="", base_price=round(price, 2), total_sales=random.randint(0, 100))
                db.add(product)
                db.flush()
                sku = SKU(product_id=product.id, spec_json='{"default":"standard"}', price=round(price, 2), stock=random.randint(20, 300))
                db.add(sku)
            db.commit()
        print(f"Created {len(shop_names_retail)} shops with products from RetailRocket")
        # Generate virtual buyers
        for i in range(settings.VIRTUAL_BUYER_COUNT):
            pref = {
                "type": random.choice(["price_sensitive", "quality_oriented", "trend_follower", "balanced"]),
                "price_weight": round(random.uniform(0.2, 0.9), 2),
                "quality_weight": round(random.uniform(0.2, 0.9), 2),
            }
            vuser = User(username=f"rbuyer_{i}", hashed_password="virtual", nickname=f"RBuyer_{i}", is_virtual=True, balance=random.uniform(5000, 50000), preferences=pref)
            db.add(vuser)
        db.commit()
        state = db.query(SimState).first()
        if not state:
            state = SimState(current_day=0)
            db.add(state)
            db.commit()
        print(f"System initialized with RetailRocket data. {settings.VIRTUAL_BUYER_COUNT} buyers created.")
    finally:
        db.close()


def load_brazilian_ecommerce(path):
    """Load Brazilian E-Commerce public dataset by Olist."""
    db = SessionLocal()
    try:
        if os.path.isdir(path):
            path = os.path.join(path, "olist_products_dataset.csv")
        print(f"Loading Brazilian dataset from {path}")
        products_file = path
        cat_file = os.path.join(os.path.dirname(path), "olist_product_category_name_translation.csv")
        # Create categories
        parent = Category(name="Brazilian E-Commerce", level=1, path="Brazilian E-Commerce")
        db.add(parent)
        db.flush()
        cats = ["health_beauty", "sports_leisure", "furniture_decor", "electronics", "clothing", "books", "toys", "home", "food", "garden"]
        cat_objs = {}
        for cname in cats:
            c = Category(name=cname.replace("_", " ").title(), level=2, parent_id=parent.id, path=f"Brazilian E-Commerce/{cname}", min_price=random.uniform(5, 30))
            db.add(c)
            db.flush()
            cat_objs[cname] = c
        db.commit()
        products_loaded = 0
        if os.path.exists(products_file):
            with open(products_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if products_loaded >= 200:
                        break
                    pcat = row.get("product_category_name", "").strip().lower()
                    if pcat and pcat in cat_objs:
                        cat = cat_objs[pcat]
                    else:
                        cat = random.choice(list(cat_objs.values()))
                    # Assign to a random virtual shop
                    vuser = User(username=f"bshop_{products_loaded % 10}", hashed_password="virtual", nickname=f"BShop_{products_loaded % 10}", is_virtual=True, is_seller=True, balance=30000)
                    db.add(vuser)
                    db.flush()
                    shop_count = db.query(Shop).filter(Shop.owner_id == vuser.id).count()
                    if shop_count == 0:
                        shop = Shop(owner_id=vuser.id, name=f"BShop_{products_loaded % 10}", description="Brazilian shop", is_virtual=True)
                        db.add(shop)
                        db.flush()
                    else:
                        shop = db.query(Shop).filter(Shop.owner_id == vuser.id).first()
                    price = float(row.get("product_length_cm", random.uniform(20, 500)))
                    price = max(10, price)
                    product = Product(shop_id=shop.id, category_id=cat.id, title=row.get("product_description", f"Brazilian Product {products_loaded}")[:200], description=row.get("product_description", "")[:500], image="", base_price=round(price, 2))
                    db.add(product)
                    db.flush()
                    sku = SKU(product_id=product.id, spec_json='{"default":"standard"}', price=round(price, 2), stock=random.randint(20, 200))
                    db.add(sku)
                    products_loaded += 1
            db.commit()
        print(f"Loaded {products_loaded} products from Brazilian dataset")
        for i in range(settings.VIRTUAL_BUYER_COUNT):
            pref = {"type": "balanced", "price_weight": round(random.uniform(0.3, 0.7), 2), "quality_weight": round(random.uniform(0.3, 0.7), 2)}
            vuser = User(username=f"bbuyer_{i}", hashed_password="virtual", nickname=f"BBuyer_{i}", is_virtual=True, balance=random.uniform(3000, 30000), preferences=pref)
            db.add(vuser)
        db.commit()
        state = db.query(SimState).first()
        if not state:
            state = SimState(current_day=0)
            db.add(state)
            db.commit()
        print("Brazilian dataset loaded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load dataset for e-commerce simulation")
    parser.add_argument("--source", choices=["retailrocket", "brazilian", "demo"], default="demo", help="Dataset source")
    parser.add_argument("--data-path", default="./data/", help="Path to dataset directory or file")
    args = parser.parse_args()
    create_tables()
    if args.source == "retailrocket":
        load_retailrocket(args.data_path)
    elif args.source == "brazilian":
        load_brazilian_ecommerce(args.data_path)
    else:
        print("Demo mode: use Celery task initialize_system_data instead")
        print("Run: celery -A app.core.celery_app call app.tasks.simulation.initialize_system_data")
