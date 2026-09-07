from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from climber_training.application.reporting import exportar_plan_pdf
from climber_training.application.services import (
    ejecutar_reevaluacion, generar_plan, guardar_perfil, listar_sesiones,
)
from climber_training.infrastructure.database import initialize_database
from climber_training.infrastructure.models import TestHistoryModel as HistoryModel

ROOT = Path(__file__).resolve().parents[2]


def test_pdf_and_test_history_are_created(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'report.db'}"); initialize_database(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory.begin() as session:
        user = guardar_perfil(session, {"alias": "Reporte", "experience_years": 2})
        plan = generar_plan(session, user_id=user.id, package_path=ROOT / "rules" / "demo", context={
            "objective": "acondicionamiento_general", "equipment": {"wall": True, "hangboard": False},
            "limitations": {"fingers": "ninguna"}, "availability": {"days": [0, 4], "max_minutes": 45},
        })
        ejecutar_reevaluacion(session, user.id, "DEMO-GENERIC", 12.5, "s", "Protocolo DEMO", plan.package_version)
        sessions = listar_sesiones(session, plan.id)
        pdf = exportar_plan_pdf(plan, sessions, tmp_path / "plan.pdf")
    assert pdf.read_bytes().startswith(b"%PDF")
    with factory() as session:
        history = list(session.scalars(select(HistoryModel).order_by(HistoryModel.id)))
        assert len(history) == 1 and history[0].result == 12.5
    engine.dispose()
