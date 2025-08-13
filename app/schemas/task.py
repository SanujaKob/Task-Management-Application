from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import date

PriorityLiteral = Literal["low", "medium", "high", "critical"]
StatusLiteral = Literal["not_started", "in_progress", "completed", "blocked"]


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    priority: PriorityLiteral = "medium"
    status: StatusLiteral = "not_started"
    progress: int = Field(0, ge=0, le=100)
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None


class TaskCreate(TaskBase):
    # All defaults from TaskBase are fine for creation
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[PriorityLiteral] = None
    status: Optional[StatusLiteral] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None


class TaskOut(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
