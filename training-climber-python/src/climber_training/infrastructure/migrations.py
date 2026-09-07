from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

from .backup import export_backup
from .config import Settings


def migrate_database(settings: Settings, alembic_root: Path) -> Path | None:
    """Actualiza a head y devuelve la copia previa creada, si fue necesaria."""
    database = settings.data_dir / "climber_training.db"
    config = Config()
    config.set_main_option("script_location", str(alembic_root))
    config.set_main_option("sqlalchemy.url", settings.database_url)
    config.attributes["database_url"] = settings.database_url
    scripts = ScriptDirectory.from_config(config)
    target = scripts.get_current_head()
    current = None
    if database.exists():
        engine = create_engine(settings.database_url)
        try:
            with engine.connect() as connection:
                current = MigrationContext.configure(connection).get_current_revision()
        finally:
            engine.dispose()
    backup = None
    if database.exists() and current != target:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup = settings.data_dir / "backups" / f"pre-migration-{current or 'unversioned'}-{stamp}.db"
        export_backup(database, backup)
    command.upgrade(config, "head")
    return backup
