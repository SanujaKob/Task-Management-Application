from fastapi import FastAPI
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from app.core.database import Base, engine, SessionLocal
from app.core.config import get_settings
from app.core.security import hash_password

from app.models.user import User, Role
from app.models.task import Task, Status
from app.models.notification import Notification

# Import router modules directly (avoid circular imports via __init__)
from app.routers import auth as auth_router
from app.routers import users as users_router
from app.routers import tasks as tasks_router
from app.routers import notifications as notifications_router


def create_app() -> FastAPI:
    app = FastAPI(title="Task Management API", version="1.0.0")

    # Create DB tables (bootstrap; migrations handled by Alembic later)
    Base.metadata.create_all(bind=engine)

    # Register routers
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(tasks_router.router)
    app.include_router(notifications_router.router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.on_event("startup")
    def seed_admin() -> None:
        """
        Create a default admin user if none exists.
        Uses ADMIN_* values from .env (loaded via pydantic-settings).
        """
        settings = get_settings()
        if not settings.admin_email or not settings.admin_password:
            return

        db = SessionLocal()
        try:
            exists = db.execute(
                select(User).where(User.role == Role.admin)
            ).scalar_one_or_none()
            if not exists:
                admin = User(
                    email=settings.admin_email,
                    full_name=settings.admin_full_name,
                    hashed_password=hash_password(settings.admin_password),
                    role=Role.admin,
                )
                db.add(admin)
                db.commit()
        finally:
            db.close()

    async def reminder_worker():
        """
        Every 60 seconds, create a notification for tasks due within 24h
        (for the assignee), skipping completed tasks and avoiding duplicates.
        """
        while True:
            try:
                now = datetime.utcnow()
                soon = now + timedelta(hours=24)

                db = SessionLocal()
                try:
                    # Find tasks with a due date within 24h and not completed
                    stmt = select(Task).where(
                        Task.due_date != None,           # noqa: E711
                        Task.status != Status.completed,
                        Task.due_date <= soon.date(),
                    )
                    tasks = db.execute(stmt).scalars().all()

                    for t in tasks:
                        if not t.assignee_id:
                            continue

                        # Avoid spamming: if a similar notification already exists, skip
                        existing = db.execute(
                            select(Notification).where(
                                Notification.user_id == t.assignee_id,
                                Notification.task_id == t.id,
                                Notification.message.like("%due within 24h%")
                            )
                        ).scalar_one_or_none()
                        if existing:
                            continue

                        msg = f"Task '{t.title}' is due within 24h (due: {t.due_date})."
                        db.add(Notification(user_id=t.assignee_id, task_id=t.id, message=msg))

                    db.commit()
                finally:
                    db.close()
            except Exception as e:
                # Keep the worker resilient—log and continue
                print(f"[reminder_worker] error: {e}")
            await asyncio.sleep(60)

    @app.on_event("startup")
    def start_background_workers():
        # Fire-and-forget background reminder loop
        asyncio.create_task(reminder_worker())

    return app


# ASGI app for Uvicorn
app = create_app()
