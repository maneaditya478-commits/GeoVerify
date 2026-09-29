"""Database setup and session management with seamless PostGIS and local SQLite fallback."""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("geoverify.db")

db_url = settings.DATABASE_URL
connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

is_connected = False
try:
    engine = create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args
    )
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    is_connected = True
    logger.info(f"Connected to primary database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
except Exception as e:
    logger.warning(f"Could not connect to configured database ({db_url}): {e}. Falling back to SQLite.")
    sqlite_url = "sqlite:///./geoverify.db"
    engine = create_engine(
        sqlite_url,
        echo=False,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
