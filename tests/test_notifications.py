from datetime import datetime
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
from app.models.notification import Notification
from app.routers.notifications import list_my_notifications, mark_read


def setup_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def test_read_status_flow():
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
        note = Notification(user_id=user.id, message="hello")
        db.add(note)
        db.commit()
        db.refresh(note)

        res = list_my_notifications(db=db, current=user)
        assert len(res) == 1
        notif = res[0]
        assert isinstance(notif.created_at, datetime)
        assert notif.read_at is None

        mark_read(notification_id=note.id, db=db, current=user)

        res = list_my_notifications(db=db, current=user)
        assert res[0].read_at is not None
