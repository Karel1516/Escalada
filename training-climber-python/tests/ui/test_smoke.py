import pytest

pytest.importorskip("PySide6")
from climber_training.ui import MainWindow


def test_main_window_smoke(qtbot):
    window = MainWindow("0.1.0-demo")
    qtbot.addWidget(window)
    window.show()
    assert window.windowTitle() == "Entrenamiento Escalada"
    assert window.navigation.count() >= 12
