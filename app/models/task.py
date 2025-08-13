from __future__ import annotations
from datetime import datetime, date
import enum

from sqlalchemy import (
    Column, Integer, String, Text, Enum, Date, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Status(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)

    priority = Column(Enum(Priority), nullable=False, default=Priority.medium)
    status = Column(Enum(Status), nullable=False, default=Status.not_started)
    progress = Column(Integer, nullable=False, default=0)  # 0..100

    due_date = Column(Date, nullable=True)

    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assignee = relationship("User")  # simple relationship; no backref for now

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
