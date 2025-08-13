from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.infrastructure.config import get_settings

settings = get_settings()
db_url = settings.database_url  # <- lowercase property

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
engine = create_engine(db_url, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
