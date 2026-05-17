"""Database session and connection management."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from doompile.db.models.tables import Base

DEFAULT_DB_PATH = Path.home() / ".doompile" / "doompile.db"


def get_db_path() -> Path:
    env_path = os.environ.get("DOOMPILE_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def get_database_url(db_path: Path | str | None = None) -> str:
    if db_path is None:
        db_path = get_db_path()
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


engine = None
SessionLocal = None


def init_engine(db_path: Path | str | None = None) -> None:
    global engine, SessionLocal
    url = get_database_url(db_path)
    engine = create_engine(url, echo=False)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_engine():
    if engine is None:
        init_engine()
    return engine


def get_session_factory() -> sessionmaker[Session]:
    if SessionLocal is None:
        init_engine()
    return SessionLocal  # type: ignore[return-value]


def get_session() -> Session:
    factory = get_session_factory()
    return factory()


SessionDep = Annotated[Session, "session"]


def create_tables() -> None:
    """Create all tables in the database."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def drop_tables() -> None:
    """Drop all tables from the database."""
    engine = get_engine()
    Base.metadata.drop_all(engine)
