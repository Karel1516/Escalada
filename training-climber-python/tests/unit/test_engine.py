from pathlib import Path

from climber_training.rule_engine import cargar_rule_package, evaluar_reglas

ROOT = Path(__file__).resolve().parents[2]


def test_safety_wins_over_performance_and_traces():
    package = cargar_rule_package(ROOT / "rules" / "demo")
    result = evaluar_reglas(package, {
        "objective": "finger_strength",
        "equipment": {"hangboard": True, "wall": True},
        "limitations": {"fingers": "limitacion"},
    }, debug=True)
    assert "DEMO_HANG" in result.excluded_exercises
    assert "DEMO_HANG" not in result.included_exercises
    assert result.values["finger_loading"] is True
    assert any(x["winner"] == "DEMO-SAFETY-001" for x in result.conflicts)
    assert {d.package_version for d in result.decisions} == {"0.1.0-demo"}
    assert result.warnings


def test_parameters_drive_prescription():
    package = cargar_rule_package(ROOT / "rules" / "demo")
    result = evaluar_reglas(package, {
        "objective": "finger_strength", "equipment": {"hangboard": True, "wall": False},
        "limitations": {"fingers": "ninguna"},
    })
    assert result.values["DEMO_HANG.sets"] == 3
    assert result.values["DEMO_HANG.rest_seconds"] == 180


def test_candidate_keeps_advanced_interventions_inside_studied_population():
    package = cargar_rule_package(ROOT / "rules" / "1.0.0-candidate")
    safe = {"fingers": "ninguna", "elbow": "ninguna", "shoulder": "ninguna"}
    advanced = evaluar_reglas(package, {
        "objective": "potencia", "level": "avanzado", "experience_years": 6,
        "equipment": {"campus_board": True, "hangboard": True, "wall": True}, "limitations": safe,
    })
    assert "CAMPUS_POWER" in advanced.included_exercises
    beginner = evaluar_reglas(package, {
        "objective": "potencia", "level": "principiante", "experience_years": 1,
        "equipment": {"campus_board": True, "hangboard": True, "wall": True}, "limitations": safe,
    })
    assert "CAMPUS_POWER" not in beginner.included_exercises


def test_candidate_finger_endurance_requires_advanced_level():
    package = cargar_rule_package(ROOT / "rules" / "1.0.0-candidate")
    result = evaluar_reglas(package, {
        "objective": "resistencia", "level": "elite", "experience_years": 8,
        "equipment": {"hangboard": True, "wall": True},
        "limitations": {"fingers": "ninguna", "elbow": "ninguna", "shoulder": "ninguna"},
    })
    assert "FINGER_ENDURANCE" in result.included_exercises
