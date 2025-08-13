from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    revoke_refresh_token,
)
from app.models.user_model import User, Role
from app.schemas.user import UserCreate, Token, TokenRefresh

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(User).where(User.email == payload.email))
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=Role.user,
    )
    db.add(user)
    db.commit()
    return {"message": "user created"}

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access = create_access_token(sub=str(user.id))
    refresh = create_refresh_token(sub=str(user.id))
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh(payload: TokenRefresh):
    try:
        sub = verify_refresh_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    revoke_refresh_token(payload.refresh_token)
    access = create_access_token(sub=sub)
    new_refresh = create_refresh_token(sub=sub)
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}
