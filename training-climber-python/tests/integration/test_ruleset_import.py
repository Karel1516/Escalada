import json
import zipfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from climber_training.infrastructure.database import initialize_database
from climber_training.infrastructure.models import RuleModel, RulePackageModel
from climber_training.infrastructure.rulesets import cargar_rule_package_db, importar_ruleset, importar_ruleset_zip
from climber_training.rule_engine import exportar_ruleset

ROOT = Path(__file__).resolve().parents[2]


def test_import_is_complete_and_immutable(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'rules.db'}")
    initialize_database(engine); factory = sessionmaker(engine)
    with factory.begin() as session:
        package = importar_ruleset(session, ROOT / "rules" / "demo")
        assert package.version == "0.1.0-demo"
        package_id = package.id
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(RuleModel)) == 6
        loaded = cargar_rule_package_db(session, package_id)
        assert len(loaded.rules) == 6
        assert loaded.version == "0.1.0-demo"
    with pytest.raises(ValueError, match="inmutable"):
        with factory.begin() as session: importar_ruleset(session, ROOT / "rules" / "demo")
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(RulePackageModel)) == 1
    engine.dispose()


def test_zip_import_and_invalid_package_leave_no_partial_rows(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'zip.db'}")
    initialize_database(engine); factory = sessionmaker(engine)
    archive = exportar_ruleset(ROOT / "rules" / "demo", tmp_path / "demo.zip")
    with factory.begin() as session: importar_ruleset_zip(session, archive)
    with factory() as session: assert session.scalar(select(func.count()).select_from(RulePackageModel)) == 1

    invalid = tmp_path / "invalid.zip"
    with zipfile.ZipFile(archive) as source, zipfile.ZipFile(invalid, "w") as target:
        for name in source.namelist():
            payload = source.read(name)
            if name == "rules.json":
                rules = json.loads(payload); rules[0]["actions"][0]["target"] = "MISSING"
                payload = json.dumps(rules).encode()
            target.writestr(name, payload)
    with pytest.raises(ValueError, match="Paquete inválido"):
        with factory.begin() as session: importar_ruleset_zip(session, invalid)
    with factory() as session: assert session.scalar(select(func.count()).select_from(RulePackageModel)) == 1
    engine.dispose()
