from typing import List, Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from task_manager_app.core.database import get_db
from task_manager_app.models.notification import Notification
from task_manager_app.models.user import User
from task_manager_app.routers.users import get_current_user
from task_manager_app.schemas.notification import NotificationOut  # <-- import BEFORE usage

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[NotificationOut])
def list_my_notifications(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum number of notifications to return")] = 100,
    offset: Annotated[int, Query(ge=0, description="Number of notifications to skip")] = 0,
):
    rows = (
        db.execute(
            select(Notification)
            .where(Notification.user_id == current.id)
            .order_by(Notification.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )
    return [NotificationOut.model_validate(n) for n in rows]


@router.post("/{notification_id}/read", status_code=204)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    db.execute(
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == current.id,
        )
        .values(read_at=datetime.utcnow())
    )
    db.commit()
    return None
