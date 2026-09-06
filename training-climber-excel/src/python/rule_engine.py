"""Deterministic reference implementation of the workbook rule engine."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

OPERATORS = {"EQ", "NEQ", "GT", "GTE", "LT", "LTE", "BETWEEN", "IN", "NOT_IN", "EXISTS", "NOT_EXISTS"}
ACTIONS = {
    "INCLUDE_EXERCISE", "EXCLUDE_EXERCISE", "INCLUDE_CATEGORY", "EXCLUDE_CATEGORY",
    "SET_SETS", "SET_REPS", "SET_DURATION", "SET_INTENSITY", "SET_REST", "SET_MIN",
    "SET_MAX", "MULTIPLY_VOLUME", "SET_FREQUENCY", "SET_LOAD", "SET_LOAD_PERCENT",
    "SET_RPE", "SET_RIR", "ALLOW_PROGRESSION", "BLOCK_PROGRESSION", "TRIGGER_DELOAD",
    "TRIGGER_REEVALUATION", "SHOW_WARNING",
}
PRECEDENCE = {"SAFETY": 500, "EXCLUSION": 400, "ELIGIBILITY": 300, "PRESCRIPTION": 200, "PREFERENCE": 100}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")


def scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    try:
        return float(text) if "." in text else int(text)
    except ValueError:
        return text


def evaluate(actual: Any, operator: str, expected: Any = "", expected2: Any = "") -> bool:
    operator = operator.upper()
    if operator == "EXISTS": return actual not in (None, "")
    if operator == "NOT_EXISTS": return actual in (None, "")
    a, b, c = scalar(actual), scalar(expected), scalar(expected2)
    if operator == "EQ": return a == b
    if operator == "NEQ": return a != b
    if operator == "GT": return a > b
    if operator == "GTE": return a >= b
    if operator == "LT": return a < b
    if operator == "LTE": return a <= b
    if operator == "BETWEEN": return b <= a <= c
    values = [scalar(x) for x in str(expected).split("|")]
    if operator == "IN": return a in values
    if operator == "NOT_IN": return a not in values
    raise ValueError(f"Operador desconocido: {operator}")


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass
class Package:
    root: Path
    meta: dict[str, Any]
    rules: list[dict[str, str]]
    conditions: list[dict[str, str]]
    actions: list[dict[str, str]]
    parameters: dict[str, Any]

    @classmethod
    def load(cls, root: str | Path) -> "Package":
        root = Path(root)
        meta = json.loads((root / "package.json").read_text(encoding="utf-8"))
        params = {r["ParameterID"]: scalar(r["Value"]) for r in rows(root / "parameters.csv")}
        return cls(root, meta, rows(root / "rules.csv"), rows(root / "conditions.csv"), rows(root / "actions.csv"), params)

    def validate(self, exercise_ids: set[str], source_ids: set[str]) -> list[str]:
        errors: list[str] = []
        version = self.meta.get("version", "")
        if not SEMVER.match(version): errors.append(f"VERSION_INVALID:{version}")
        ids = [r["RuleID"] for r in self.rules]
        for rid in sorted({x for x in ids if ids.count(x) > 1}): errors.append(f"RULE_DUPLICATE:{rid}")
        known = set(ids)
        for c in self.conditions:
            if c["RuleID"] not in known: errors.append(f"RULE_MISSING:{c['RuleID']}")
            if c["Operator"] not in OPERATORS: errors.append(f"OPERATOR_INVALID:{c['Operator']}")
            if c["Operator"] == "BETWEEN":
                try:
                    if scalar(c["Value1"]) > scalar(c["Value2"]): errors.append(f"RANGE_INVALID:{c['RuleID']}")
                except TypeError: errors.append(f"TYPE_INVALID:{c['RuleID']}")
        for a in self.actions:
            if a["ActionType"] not in ACTIONS: errors.append(f"ACTION_INVALID:{a['ActionType']}")
            if a["Value"].startswith("PARAM:") and a["Value"][6:] not in self.parameters:
                errors.append(f"PARAMETER_MISSING:{a['Value'][6:]}")
            if a["ActionType"].endswith("EXERCISE") and a["Target"] not in exercise_ids:
                errors.append(f"EXERCISE_MISSING:{a['Target']}")
        for r in self.rules:
            try: int(r["Priority"])
            except ValueError: errors.append(f"PRIORITY_INVALID:{r['RuleID']}")
            sources = {x for x in r.get("SourceIDs", "").split("|") if x}
            for sid in sources - source_ids: errors.append(f"SOURCE_MISSING:{sid}")
            if not sources and not r.get("Rationale", "").strip(): errors.append(f"ORIGIN_MISSING:{r['RuleID']}")
        return sorted(set(errors))


class Engine:
    def __init__(self, package: Package): self.package = package

    def matched_rules(self, context: dict[str, Any]) -> list[dict[str, str]]:
        output = []
        for rule in self.package.rules:
            if str(rule.get("Enabled", "TRUE")).upper() != "TRUE": continue
            conds = [c for c in self.package.conditions if c["RuleID"] == rule["RuleID"]]
            groups: dict[str, list[bool]] = {}
            for c in conds:
                groups.setdefault(c.get("GroupID", "1"), []).append(evaluate(context.get(c["Field"]), c["Operator"], c["Value1"], c["Value2"]))
            if not conds or any(all(values) for values in groups.values()): output.append(rule)
        return output

    def proposals(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        result = []
        for rule in self.matched_rules(context):
            for action in (a for a in self.package.actions if a["RuleID"] == rule["RuleID"]):
                value = action["Value"]
                if value.startswith("PARAM:"): value = self.package.parameters[value[6:]]
                result.append({**action, "Value": scalar(value), "RuleType": rule["RuleType"], "Priority": int(rule["Priority"])})
        return sorted(result, key=lambda x: (-PRECEDENCE.get(x["RuleType"], 0), -x["Priority"], x["RuleID"], x["ActionID"]))

    def resolve(self, context: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        state: dict[str, Any] = {"included": [], "excluded": [], "warnings": [], "prescription": {}}
        decisions = []
        locked: set[str] = set()
        for p in self.proposals(context):
            key = f"{p['ActionType'].replace('INCLUDE_', '').replace('EXCLUDE_', '')}:{p['Target']}"
            previous = None
            applied = True
            if key in locked and p["RuleType"] != "SAFETY": applied = False
            elif p["ActionType"] == "EXCLUDE_EXERCISE":
                state["excluded"].append(p["Target"]); locked.add(key)
            elif p["ActionType"] == "INCLUDE_EXERCISE" and p["Target"] not in state["excluded"]:
                state["included"].append(p["Target"])
            elif p["ActionType"] == "SHOW_WARNING": state["warnings"].append(str(p["Value"]))
            elif p["ActionType"].startswith("SET_"):
                field = p["ActionType"][4:].lower(); previous = state["prescription"].get(field); state["prescription"][field] = p["Value"]
            elif p["ActionType"] == "BLOCK_PROGRESSION": state["prescription"]["progression"] = "BLOCK"
            elif p["ActionType"] == "ALLOW_PROGRESSION" and state["prescription"].get("progression") != "BLOCK": state["prescription"]["progression"] = "ALLOW"
            elif p["ActionType"] == "TRIGGER_DELOAD": state["prescription"]["progression"] = "DELOAD"
            elif p["ActionType"] == "TRIGGER_REEVALUATION": state["prescription"]["progression"] = "REEVALUATE"
            decisions.append({"RuleID": p["RuleID"], "Action": p["ActionType"], "Target": p["Target"], "PreviousValue": previous, "NewValue": p["Value"], "Applied": applied})
        state["included"] = sorted(set(state["included"]) - set(state["excluded"]))
        state["excluded"] = sorted(set(state["excluded"]))
        return state, decisions

    def generate_week(self, context: dict[str, Any], exercises: list[dict[str, str]]) -> dict[str, Any]:
        state, decisions = self.resolve(context)
        available = {x.strip() for x in str(context.get("Equipment", "")).split("|") if x.strip()}
        by_id = {e["ExerciseID"]: e for e in exercises}
        selected = []
        for eid in state["included"]:
            e = by_id[eid]
            required = {x for x in e["Equipment"].split("|") if x}
            if required <= available or not required: selected.append(e)
        days = max(1, int(context.get("DaysAvailable", 2)))
        budget = int(context.get("SessionMinutes", 60))
        sessions = [{"Day": i + 1, "Exercises": [], "Minutes": 0} for i in range(days)]
        for i, e in enumerate(selected):
            session = sessions[i % days]
            minutes = int(e["EstimatedMinutes"])
            if session["Minutes"] + minutes <= budget:
                session["Exercises"].append({**e, **state["prescription"]})
                session["Minutes"] += minutes
        return {"RulePackageVersionUsed": self.package.meta["version"], "Generated": date.today().isoformat(), "Sessions": sessions, "Warnings": state["warnings"], "Decisions": decisions}
