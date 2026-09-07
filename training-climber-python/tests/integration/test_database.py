from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from climber_training.application.services import generar_plan, guardar_perfil, mostrar_trazabilidad
from climber_training.infrastructure.database import initialize_database
from climber_training.infrastructure.models import UserModel


def test_profile_persists_in_transaction(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    initialize_database(engine)
    factory = sessionmaker(engine)
    with factory.begin() as session:
        user = guardar_perfil(session, {"alias": "Luna", "age": 25, "experience_years": 2})
        assert user.id
    with factory() as session:
        assert session.scalar(select(UserModel).where(UserModel.alias == "Luna")) is not None
    engine.dispose()


def test_plan_is_persisted_with_snapshot_and_trace(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'plan.db'}")
    initialize_database(engine)
    factory = sessionmaker(engine)
    package = Path(__file__).resolve().parents[2] / "rules" / "demo"
    with factory.begin() as session:
        user = guardar_perfil(session, {"alias": "Sol", "experience_years": 3})
        plan = generar_plan(session, user_id=user.id, package_path=package, context={
            "objective": "finger_strength",
            "equipment": {"hangboard": True, "wall": True},
            "limitations": {"fingers": "ninguna"},
            "availability": {"days": [0, 3], "max_minutes": 45},
        })
        assert plan.package_version == "0.1.0-demo"
        assert len(mostrar_trazabilidad(session, plan.id)) >= 3
    engine.dispose()
