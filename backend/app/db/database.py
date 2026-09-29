"""Database setup and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# If Postgres is configured, use it. If connection fails or sqlite is requested, fallback to SQLite.
db_url = settings.DATABASE_URL

connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args
    )
except Exception:
    # Fallback to local SQLite if postgres connection initialization fails
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
