from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from climber_training.domain.entities import Action, Condition, ConditionGroup, Rule, RulePackage
from climber_training.domain.enums import ActionType, Operator, PackageStatus, RuleType

SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")


def _condition(data: dict[str, Any]) -> Condition | ConditionGroup:
    if "conditions" in data:
        return ConditionGroup(data["combinator"], tuple(_condition(x) for x in data["conditions"]))
    return Condition(data["field"], Operator(data["operator"]), data.get("value"))


def cargar_rule_package(path: str | Path) -> RulePackage:
    root = Path(path)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    data = json.loads((root / "rules.json").read_text(encoding="utf-8"))
    params = json.loads((root / "parameters.json").read_text(encoding="utf-8"))
    exercises = json.loads((root / "exercises.json").read_text(encoding="utf-8"))
    evidence = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
    rules = []
    for item in data:
        rules.append(Rule(
            rule_id=item["rule_id"], rule_type=RuleType(item["rule_type"]),
            priority=item["priority"], condition=_condition(item["condition"]),
            actions=tuple(Action(ActionType(a["action_type"]), a["target"], a.get("value"), a.get("parameter_id")) for a in item["actions"]),
            rationale=item["rationale"], classification=item["classification"],
            evidence_status=item["evidence_status"],
        ))
    return RulePackage(
        package_id=manifest["package_id"], version=manifest["version"], status=manifest["status"],
        schema_version=manifest["schema_version"], parameters={p["parameter_id"]: p["value"] for p in params},
        exercises=frozenset(e["exercise_id"] for e in exercises),
        evidence=frozenset(e["source_id"] for e in evidence), rules=tuple(rules), manifest=manifest,
    )


def validate_rule_package(path: str | Path) -> list[str]:
    root = Path(path)
    errors: list[str] = []
    required = ("manifest.json", "rules.json", "parameters.json", "exercises.json", "evidence.json", "rule_evidence.json")
    for name in required:
        if not (root / name).is_file():
            errors.append(f"Missing file: {name}")
    if errors:
        return errors
    try:
        schema_root = root.parent / "schema"
        if not schema_root.is_dir():
            schema_root = Path(__file__).resolve().parents[3] / "rules" / "schema"
        schema_files = (
            ("manifest.json", "package.schema.json"),
            ("rules.json", "rules.schema.json"),
            ("parameters.json", "parameters.schema.json"),
            ("exercises.json", "exercises.schema.json"),
            ("evidence.json", "evidence.schema.json"),
            ("rule_evidence.json", "rule_evidence.schema.json"),
        )
        for filename, schema_name in schema_files:
            instance = json.loads((root / filename).read_text(encoding="utf-8"))
            schema = json.loads((schema_root / schema_name).read_text(encoding="utf-8"))
            for issue in Draft202012Validator(schema).iter_errors(instance):
                location = ".".join(str(x) for x in issue.absolute_path) or "$"
                errors.append(f"{filename}:{location}: {issue.message}")
        package = cargar_rule_package(root)
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        return [f"Invalid package data: {exc}"]
    if not SEMVER.fullmatch(package.version):
        errors.append(f"Invalid semantic version: {package.version}")
    if package.status not in set(PackageStatus):
        errors.append(f"Invalid status: {package.status}")
    ids = [r.rule_id for r in package.rules]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate RuleID")
    for rule in package.rules:
        if not 0 <= rule.priority <= 10000:
            errors.append(f"{rule.rule_id}: invalid priority")
        if not rule.rationale.strip():
            errors.append(f"{rule.rule_id}: missing rationale")
        if not rule.classification.strip():
            errors.append(f"{rule.rule_id}: missing classification")
        for action in rule.actions:
            if action.parameter_id and action.parameter_id not in package.parameters:
                errors.append(f"{rule.rule_id}: unknown ParameterID {action.parameter_id}")
            if action.action_type in {ActionType.INCLUDE_EXERCISE, ActionType.EXCLUDE_EXERCISE} and action.target not in package.exercises:
                errors.append(f"{rule.rule_id}: unknown ExerciseID {action.target}")
    mappings = json.loads((root / "rule_evidence.json").read_text(encoding="utf-8"))
    mapped_rule_ids: set[str] = set()
    for mapping in mappings:
        if mapping["rule_id"] not in ids:
            errors.append(f"Broken RuleID reference: {mapping['rule_id']}")
        if mapping["source_id"] not in package.evidence:
            errors.append(f"Broken SourceID reference: {mapping['source_id']}")
        mapped_rule_ids.add(mapping["rule_id"])
    for rule in package.rules:
        if rule.classification in {"DIRECT_EVIDENCE", "INDIRECT_EVIDENCE"} and rule.rule_id not in mapped_rule_ids:
            errors.append(f"{rule.rule_id}: evidence classification requires a rule_evidence mapping")
    checksums = package.manifest.get("checksums", {})
    for name, expected in checksums.items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"Checksum mismatch: {name}")
    if package.status == PackageStatus.ACTIVE and errors:
        errors.append("Invalid package cannot be ACTIVE")
    return errors


def exportar_ruleset(source: str | Path, destination: str | Path) -> Path:
    root, target = Path(source), Path(destination)
    errors = validate_rule_package(root)
    if errors:
        raise ValueError("; ".join(errors))
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(root.glob("*.json"), key=lambda p: p.name):
            info = zipfile.ZipInfo(path.name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
    return target
