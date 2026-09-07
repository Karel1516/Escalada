from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from .config import Settings
from .models import Base


def build_engine(settings: Settings | None = None):
    engine = create_engine((settings or Settings.load()).database_url, future=True)
    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON"))
    return engine


def initialize_database(engine) -> None:
    Base.metadata.create_all(engine)


@contextmanager
def transaction(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        with session.begin():
            yield session
    finally:
        session.close()
