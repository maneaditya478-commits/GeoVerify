"""API dependencies."""

from app.db.database import get_db

# Export get_db for route injections
__all__ = ["get_db"]
