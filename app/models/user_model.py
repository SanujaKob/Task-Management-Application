from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum

class Role(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    user = "user"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.user)
