"""
Database connection and session management.
Uses SQLAlchemy async engine pointed at Supabase PostgreSQL.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/stocksense")

# Defaults to SQLAlchemy's pool settings; tune pool_size/max_overflow for production.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=True, **({} if not connect_args else {"connect_args": connect_args}))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, auto-closes on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
