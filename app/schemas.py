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

from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: str
    status: Optional[str] = "Not Started"
    due_date: Optional[datetime] = None
    assigned_to: int  # User ID

class TaskCreate(TaskBase):
    pass  # Use all fields from TaskBase

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskOut(TaskBase):
    id: int

    class Config:
        orm_mode = True
