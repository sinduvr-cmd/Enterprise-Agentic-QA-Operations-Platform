"""
Database connection and session management for SQLAlchemy.
Supports both PostgreSQL (enterprise/production) and SQLite (instant local development).
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.config import settings

logger = logging.getLogger(__name__)

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL production pool settings
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a transactional database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables in the database and seeds realistic demo data if empty.
    """
    # Import all models to ensure they are registered with Base.metadata
    from backend.app.models import (  # noqa: F401
        user,
        project,
        requirement,
        test_case,
        automation_script,
        workflow,
        approval,
        execution,
        audit,
    )
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")

    if settings.DEMO_MODE:
        from backend.app.services.seed_service import seed_demonstration_data
        db = SessionLocal()
        try:
            seed_demonstration_data(db)
        finally:
            db.close()
