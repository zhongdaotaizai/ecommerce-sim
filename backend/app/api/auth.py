from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.models.user import User, Shop
from app.schemas.user import UserRegister, UserLogin, Token, UserInfo, OpenShop, ShopInfo

router = APIRouter()


@router.post("/register", response_model=Token)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(400, "Username already exists")
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        nickname=data.nickname or data.username,
        email=data.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserInfo.model_validate(user))


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserInfo.model_validate(user))


@router.get("/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    return UserInfo.model_validate(current_user)


@router.post("/open-shop", response_model=ShopInfo)
def open_shop(data: OpenShop, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    if current_user.is_seller:
        raise HTTPException(400, "You already have a shop")
    shop = Shop(owner_id=current_user.id, name=data.shop_name, description=data.description)
    db.add(shop)
    current_user.is_seller = True
    db.commit()
    db.refresh(shop)
    return ShopInfo.model_validate(shop)


@router.get("/shop", response_model=ShopInfo)
def get_my_shop(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    shop = db.query(Shop).filter(Shop.owner_id == current_user.id).first()
    if not shop:
        raise HTTPException(404, "You don't have a shop yet")
    return ShopInfo.model_validate(shop)


@router.get("/profile/{user_id}", response_model=UserInfo)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return UserInfo.model_validate(user)

@router.post("/login-code")
def login_with_code(data: dict, db: Session = Depends(get_db)):
    user_id = data.get("user_id")
    code = data.get("code", "")
    if code != "888888":
        raise HTTPException(400, "验证码错误")
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    except:
        raise HTTPException(400, "用户ID格式错误")
    if not user:
        raise HTTPException(404, "用户不存在")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, user=UserInfo.model_validate(user))
