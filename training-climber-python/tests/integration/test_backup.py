import sqlite3

import pytest

from climber_training.infrastructure.backup import export_backup, restore_backup


def test_backup_and_atomic_restore(tmp_path):
    database, backup = tmp_path / "app.db", tmp_path / "backup.db"
    connection = sqlite3.connect(database)
    connection.execute("create table users(id integer primary key, alias text)")
    connection.execute("insert into users(alias) values ('original')"); connection.commit(); connection.close()
    export_backup(database, backup)
    connection = sqlite3.connect(database); connection.execute("insert into users(alias) values ('later')"); connection.commit(); connection.close()
    restore_backup(backup, database)
    connection = sqlite3.connect(database)
    assert connection.execute("select alias from users order by id").fetchall() == [("original",)]
    connection.close()


def test_restore_rejects_foreign_database(tmp_path):
    foreign = tmp_path / "foreign.db"; destination = tmp_path / "app.db"
    connection = sqlite3.connect(foreign); connection.execute("create table other(id integer)"); connection.close()
    with pytest.raises(ValueError, match="no pertenece"):
        restore_backup(foreign, destination)
    assert not destination.exists()
