from __future__ import annotations

import csv
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "python"))
from rule_engine import Engine, Package, evaluate  # noqa: E402


def load_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


EXERCISES = load_csv(ROOT / "evidence" / "exercises.csv")
EVIDENCE = load_csv(ROOT / "evidence" / "evidence.csv")
EIDS = {x["ExerciseID"] for x in EXERCISES}
SIDS = {x["SourceID"] for x in EVIDENCE}
RESULTS: list[tuple[str, bool, str]] = []


def check(name, condition, detail=""):
    RESULTS.append((name, bool(condition), detail))
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def main():
    cases = [
        ("EQ", 2, "2", "", True), ("NEQ", 2, 3, "", True),
        ("GT", 3, 2, "", True), ("GTE", 2, 2, "", True),
        ("LT", 1, 2, "", True), ("LTE", 2, 2, "", True),
        ("BETWEEN", 2, 1, 3, True), ("IN", "b", "a|b|c", "", True),
        ("NOT_IN", "z", "a|b|c", "", True), ("EXISTS", "x", "", "", True),
        ("NOT_EXISTS", "", "", "", True),
    ]
    for op, actual, v1, v2, expected in cases:
        check(f"operator_{op}", evaluate(actual, op, v1, v2) == expected)

    demo = Package.load(ROOT / "rules" / "demo")
    candidate = Package.load(ROOT / "rules" / "1.0.0-candidate")
    check("demo_valid", demo.validate(EIDS, SIDS) == [], str(demo.validate(EIDS, SIDS)))
    check("candidate_valid", candidate.validate(EIDS, SIDS) == [], str(candidate.validate(EIDS, SIDS)))

    engine = Engine(demo)
    base = {"PrimaryObjective": "Fuerza de dedos", "ExperienceYears": 3, "Equipment": "Hangboard", "FingerPain": 0,
            "PainStatus": "ninguna", "Completion": 95, "SessionRPE": 7, "DaysAvailable": 2, "SessionMinutes": 45}
    state, decisions = engine.resolve(base)
    check("and_conditions", "EX_HANG_MAX" in state["included"])
    check("parameter_resolution", state["prescription"]["sets"] == 3)
    check("traceability", any(d["RuleID"] == "D-SEL-002" for d in decisions))
    painful = {**base, "FingerPain": 2}
    state, decisions = engine.resolve(painful)
    check("safety_beats_performance", "EX_HANG_MAX" in state["excluded"] and "EX_HANG_MAX" not in state["included"])
    check("safety_blocks_progression", state["prescription"]["progression"] == "BLOCK")
    week = engine.generate_week(base, EXERCISES)
    check("time_budget", all(s["Minutes"] <= 45 for s in week["Sessions"]))
    check("version_pinned", week["RulePackageVersionUsed"] == demo.meta["version"])

    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / "broken"
        shutil.copytree(ROOT / "rules" / "demo", broken)
        p = broken / "actions.csv"
        p.write_text(p.read_text(encoding="utf-8").replace("PARAM:P_SETS", "PARAM:NOPE"), encoding="utf-8")
        check("missing_parameter", any(x == "PARAMETER_MISSING:NOPE" for x in Package.load(broken).validate(EIDS, SIDS)))
        shutil.rmtree(broken)
        shutil.copytree(ROOT / "rules" / "demo", broken)
        p = broken / "rules.csv"
        text = p.read_text(encoding="utf-8")
        text = text.replace("D-SAFE-001,SAFETY,1000,Bloquear hangboard con dolor de dedos,SAFETY_PRECAUTION,UNCERTAIN,E005,", "D-SAFE-001,SAFETY,1000,Bloquear hangboard con dolor de dedos,SAFETY_PRECAUTION,UNCERTAIN,NOPE,")
        p.write_text(text, encoding="utf-8")
        check("missing_source", any(x == "SOURCE_MISSING:NOPE" for x in Package.load(broken).validate(EIDS, SIDS)))

    passed = sum(ok for _, ok, _ in RESULTS)
    print(f"PASS {passed}/{len(RESULTS)}")
    for name, ok, detail in RESULTS: print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")


if __name__ == "__main__":
    main()
