"""Database wiring wrapper.

The canonical implementation currently lives in `app.database`.
This module exists to support the target folder structure without moving working code yet.
"""

from app.database import Base, SessionLocal, engine, get_db  # noqa: F401

