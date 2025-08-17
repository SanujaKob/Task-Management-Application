from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from task_manager_app.core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session_once():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
