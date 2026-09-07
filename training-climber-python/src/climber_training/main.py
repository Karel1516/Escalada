from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from climber_training.infrastructure import build_engine
from climber_training.infrastructure.config import Settings
from climber_training.infrastructure.migrations import migrate_database
from climber_training.infrastructure.models import RulePackageModel, TestModel
from climber_training.infrastructure.rulesets import importar_ruleset
from climber_training.ui import MainWindow
from sqlalchemy.orm import sessionmaker


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[2]


def main() -> int:
    app = QApplication(sys.argv)
    settings = None
    try:
        settings = Settings.load()
        migrate_database(settings, resource_root() / "alembic")
        engine = build_engine(settings)
        factory = sessionmaker(engine, expire_on_commit=False)
        with factory.begin() as session:
            exists = session.query(RulePackageModel).filter_by(
                package_id="climber-training-demo", version="0.1.0-demo"
            ).first()
            if exists is None:
                importar_ruleset(session, resource_root() / "rules" / "demo")
            if session.query(TestModel).filter_by(test_id="DEMO-GENERIC").first() is None:
                session.add(TestModel(
                    test_id="DEMO-GENERIC", name="Evaluación técnica DEMO",
                    protocol="Registra un valor reproducible con la misma unidad y protocolo. No tiene interpretación deportiva.",
                    eligibility={"purpose": "software_test"}, source_id="DESIGN-001",
                ))
    except Exception as exc:  # top-level boundary: user-readable failure
        if settings is not None:
            (settings.data_dir / "startup-error.log").write_text(traceback.format_exc(), encoding="utf-8")
        QMessageBox.critical(None, "Error de inicio", f"No se pudo abrir la base de datos:\n{exc}")
        return 1
    window = MainWindow(
        package_version="0.1.0-demo",
        session_factory=factory,
        package_path=resource_root() / "rules" / "demo",
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
