import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure the app package is on the import path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base
from app.core.security import hash_password
from app.models.user import User, Role
from app.models.task import Task
from app.models.notification import Notification
from app.routers.tasks_router import list_tasks
from app.routers.notifications_router import list_my_notifications


def setup_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_task_pagination():
    SessionLocal = setup_session()
    with SessionLocal() as db:
        user = User(
            email="user@example.com",
            full_name="Test User",
            hashed_password=hash_password("pass"),
            role=Role.user,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        for i in range(3):
            db.add(Task(title=f"task-{i}", assignee_id=user.id))
        db.commit()

        res = list_tasks(db=db, current=user, limit=2)
        assert len(res) == 2
        assert res[0].title == "task-0"
        assert res[1].title == "task-1"

        res = list_tasks(db=db, current=user, limit=2, offset=1)
        assert len(res) == 2
        assert res[0].title == "task-1"
        assert res[1].title == "task-2"


def test_notification_pagination():
    SessionLocal = setup_session()
    with SessionLocal() as db:
        user = User(
            email="user@example.com",
            full_name="Test User",
            hashed_password=hash_password("pass"),
            role=Role.user,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        for i in range(3):
            db.add(Notification(user_id=user.id, message=f"note-{i}"))
        db.commit()

        res = list_my_notifications(db=db, current=user, limit=2)
        assert [n.message for n in res] == ["note-2", "note-1"]

        res = list_my_notifications(db=db, current=user, limit=1, offset=2)
        assert len(res) == 1
        assert res[0].message == "note-0"
