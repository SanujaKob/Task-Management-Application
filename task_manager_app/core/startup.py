# core/startup.py
from fastapi import FastAPI
from sqlalchemy.orm import Session
from .deps import get_db_session_once
from ..models import Role, User
from ..core.security import get_password_hash

def on_startup(app: FastAPI):
    @app.on_event("startup")
    async def seed_roles_and_admin():
        db: Session = next(get_db_session_once())
        for name in ["Admin", "Manager", "User"]:
            if not db.query(Role).filter_by(name=name).first():
                db.add(Role(name=name))
        db.commit()
        # Optional: ensure one admin exists
        if not db.query(User).join(Role).filter(Role.name=="Admin").first():
            admin = User(email="admin@example.com",
                         hashed_password=get_password_hash("Admin@123"))
            admin.roles = [db.query(Role).filter_by(name="Admin").first()]
            db.add(admin); db.commit()
