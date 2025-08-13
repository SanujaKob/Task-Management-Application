from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from task_manager_app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory store for revoked refresh tokens
revoked_refresh_tokens: set[str] = set()

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(sub: str, minutes: int | None = None) -> str:
    exp_minutes = minutes or settings.access_token_expire_minutes
    payload = {"sub": sub, "exp": datetime.utcnow() + timedelta(minutes=exp_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return str(payload.get("sub"))

def create_refresh_token(sub: str, days: int | None = None) -> str:
    exp_days = days or settings.refresh_token_expire_days
    payload = {
        "sub": sub,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=exp_days),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_refresh_token(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")
    return str(payload.get("sub"))

def verify_refresh_token(token: str) -> str:
    if token in revoked_refresh_tokens:
        raise JWTError("Token revoked")
    return decode_refresh_token(token)

def revoke_refresh_token(token: str) -> None:
    revoked_refresh_tokens.add(token)
