"""
Shared FastAPI dependencies.
"""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, closing it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
