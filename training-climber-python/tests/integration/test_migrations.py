from pathlib import Path

from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from climber_training.infrastructure.config import Settings
from climber_training.infrastructure.database import initialize_database
from climber_training.infrastructure.migrations import migrate_database


def test_programmatic_migration_reaches_head_and_is_idempotent(tmp_path):
    database = tmp_path / "climber_training.db"
    settings = Settings(tmp_path, f"sqlite:///{database.as_posix()}")
    alembic_root = Path(__file__).resolve().parents[2] / "alembic"
    assert migrate_database(settings, alembic_root) is None


def test_unversioned_database_is_backed_up_before_upgrade(tmp_path):
    database = tmp_path / "climber_training.db"
    settings = Settings(tmp_path, f"sqlite:///{database.as_posix()}")
    engine = create_engine(settings.database_url); initialize_database(engine); engine.dispose()
    alembic_root = Path(__file__).resolve().parents[2] / "alembic"
    backup = migrate_database(settings, alembic_root)
    assert backup is not None and backup.is_file()
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        assert MigrationContext.configure(connection).get_current_revision() == "0002"
    engine.dispose()
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        assert MigrationContext.configure(connection).get_current_revision() == "0002"
        assert "population" in {item["name"] for item in inspect(connection).get_columns("evidence")}
    engine.dispose()
    assert migrate_database(settings, alembic_root) is None
