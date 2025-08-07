from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "employee"

class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True
