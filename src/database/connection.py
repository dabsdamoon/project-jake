"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

from src.models.schemas import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jake.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Session:
    """
    Context manager for database sessions

    Usage:
        with get_db() as db:
            # do database operations
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get database session (for FastAPI dependency injection)

    Usage:
        def endpoint(db: Session = Depends(get_db_session)):
            # use db
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
