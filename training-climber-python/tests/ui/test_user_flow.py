from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from climber_training.infrastructure.database import initialize_database
from climber_training.infrastructure.models import DecisionLogModel, PlanModel, SessionFeedbackModel, UserModel
from climber_training.infrastructure.rulesets import importar_ruleset
from climber_training.ui import MainWindow

ROOT = Path(__file__).resolve().parents[2]


def button(window, text):
    return next(item for item in window.findChildren(QPushButton) if item.text() == text)


def test_complete_primary_user_flow(qtbot, tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'ui.db'}"); initialize_database(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory.begin() as session: importar_ruleset(session, ROOT / "rules" / "demo")
    window = MainWindow("0.1.0-demo", factory, ROOT / "rules" / "demo")
    qtbot.addWidget(window); window.show()

    window.alias.setText("Ariadna"); window.experience.setValue(3)
    qtbot.mouseClick(button(window, "Guardar nuevo perfil"), Qt.MouseButton.LeftButton)
    assert window.current_user_id is not None
    window.objective.setCurrentText("finger_strength"); window.wall.setChecked(True); window.hangboard.setChecked(True)
    qtbot.mouseClick(button(window, "Guardar contexto"), Qt.MouseButton.LeftButton)
    qtbot.mouseClick(button(window, "Generar plan auditable"), Qt.MouseButton.LeftButton)
    assert window.plan_table.rowCount() == 2
    assert window.history_table.rowCount() >= 3
    qtbot.mouseClick(button(window, "Registrar sin sobrescribir"), Qt.MouseButton.LeftButton)
    assert "registrado" in window.feedback_message.text()

    with factory() as session:
        assert session.scalar(select(func.count()).select_from(UserModel)) == 1
        assert session.scalar(select(func.count()).select_from(PlanModel)) == 1
        assert session.scalar(select(func.count()).select_from(DecisionLogModel)) >= 3
        assert session.scalar(select(func.count()).select_from(SessionFeedbackModel)) == 1
    window.close(); engine.dispose()
