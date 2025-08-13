from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal

RoleLiteral = Literal["admin", "manager", "user"]

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: RoleLiteral = "user"

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(min_length=6)

class UserOut(UserBase):
    id: int
    # Pydantic v2: use model_config instead of class Config
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str
