from __future__ import annotations

import json
import os
import shutil
import sqlite3
import tempfile
from datetime import UTC, datetime
from pathlib import Path


def export_backup(database: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(database)
    target = sqlite3.connect(destination)
    try:
        source.backup(target)
        target.execute("PRAGMA integrity_check").fetchone()
    finally:
        source.close(); target.close()
    return destination


def restore_backup(backup: Path, database: Path) -> None:
    check = sqlite3.connect(f"file:{backup.as_posix()}?mode=ro", uri=True)
    try:
        result = check.execute("PRAGMA integrity_check").fetchone()
        if not result or result[0] != "ok":
            raise ValueError("La copia no supera PRAGMA integrity_check")
        tables = {row[0] for row in check.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "alembic_version" not in tables and "users" not in tables:
            raise ValueError("La copia no pertenece a Climber Training")
    finally:
        check.close()
    database.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=database.parent, suffix=".restore") as handle:
        temporary = Path(handle.name)
    try:
        shutil.copy2(backup, temporary)
        os.replace(temporary, database)
    finally:
        temporary.unlink(missing_ok=True)
