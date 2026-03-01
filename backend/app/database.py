# Compatibility shim — re-exports from app.db.session
# Some models use `from app.database import Base` (legacy pattern)
# The canonical database setup lives in app/db/session.py
from app.db.session import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
