from dataclasses import replace
from pathlib import Path

import pytest

from climber_training.rule_engine import cargar_rule_package, evaluar_reglas

ROOT = Path(__file__).resolve().parents[2]


def context(*, days, minutes, level, objective, wall=True, hangboard=False, fingers="ninguna", experience=1):
    return {
        "availability": {"days": days, "max_minutes": minutes}, "level": level,
        "objective": objective, "equipment": {"wall": wall, "hangboard": hangboard},
        "limitations": {"fingers": fingers}, "experience_years": experience,
    }


@pytest.mark.parametrize("case", [
    context(days=[1, 5], minutes=60, level="principiante", objective="acondicionamiento_general", hangboard=False),
    context(days=[0, 2, 5], minutes=75, level="intermedio", objective="finger_strength", hangboard=True, experience=3),
    context(days=[0, 1, 3, 5], minutes=90, level="avanzado", objective="potencia", hangboard=True, experience=6),
    context(days=[0, 3], minutes=60, level="intermedio", objective="finger_strength", hangboard=True, fingers="limitacion", experience=4),
    context(days=[2, 6], minutes=45, level="intermedio", objective="acondicionamiento_general"),
])
def test_cases_a_to_e_are_deterministic_and_safe(case):
    package = cargar_rule_package(ROOT / "rules" / "demo")
    first = evaluar_reglas(package, case); second = evaluar_reglas(package, case)
    assert first.values == second.values
    assert first.included_exercises == second.included_exercises
    if case["limitations"]["fingers"] == "limitacion":
        assert "DEMO_HANG" in first.excluded_exercises


def test_case_f_historical_version_is_preserved():
    one = cargar_rule_package(ROOT / "rules" / "demo")
    two = replace(one, version="0.2.0-demo")
    data = context(days=[0, 3], minutes=60, level="intermedio", objective="finger_strength", hangboard=True)
    assert {d.package_version for d in evaluar_reglas(one, data).decisions} == {"0.1.0-demo"}
    assert {d.package_version for d in evaluar_reglas(two, data).decisions} == {"0.2.0-demo"}


def test_feedback_can_progress_deload_or_stop():
    package = cargar_rule_package(ROOT / "rules" / "demo")
    base = context(days=[0, 3], minutes=60, level="intermedio", objective="finger_strength", hangboard=True)
    progress = evaluar_reglas(package, base | {"feedback": {"completion_percent": 95, "rpe": 7, "fatigue": 4, "pain": 1}})
    assert progress.values["progression.decision"] == "PROGRESS"
    deload = evaluar_reglas(package, base | {"feedback": {"completion_percent": 70, "rpe": 9, "fatigue": 9, "pain": 1}})
    assert deload.values["progression.deload"] is True
    stop = evaluar_reglas(package, base | {"feedback": {"completion_percent": 95, "rpe": 7, "fatigue": 4, "pain": 5}})
    assert stop.values["progression.decision"] == "STOP"
    assert stop.values["progression.reevaluate"] is True
