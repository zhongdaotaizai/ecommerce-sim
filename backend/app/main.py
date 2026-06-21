from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import auth, product, cart, order, market, simulate, wallet
import os

app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME}

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(product.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(order.router, prefix="/api/orders", tags=["Orders"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(simulate.router, prefix="/api/simulate", tags=["Simulation"])
app.include_router(wallet.router, prefix="/api/wallet", tags=["Wallet"])

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

@app.get("/")
def root():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="text/html")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
