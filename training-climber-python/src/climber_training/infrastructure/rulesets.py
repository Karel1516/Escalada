from __future__ import annotations

import json
import tempfile
import zipfile
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from climber_training.infrastructure.models import (
    EvidenceModel, ExerciseModel, ParameterModel, RuleActionModel,
    RuleConditionModel, RuleEvidenceModel, RuleModel, RulePackageModel,
)
from climber_training.domain.entities import Action, Condition, ConditionGroup, Rule, RulePackage
from climber_training.domain.enums import ActionType, Operator, RuleType
from climber_training.rule_engine import validate_rule_package

REQUIRED_FILES = {
    "manifest.json", "rules.json", "parameters.json", "exercises.json",
    "evidence.json", "rule_evidence.json",
}
MAX_PACKAGE_BYTES = 10 * 1024 * 1024


def _read(root: Path, name: str) -> Any:
    return json.loads((root / name).read_text(encoding="utf-8"))


def _condition_from_payload(data: dict[str, Any]) -> Condition | ConditionGroup:
    if "conditions" in data:
        return ConditionGroup(data["combinator"], tuple(_condition_from_payload(x) for x in data["conditions"]))
    return Condition(data["field"], Operator(data["operator"]), data.get("value"))


def cargar_rule_package_db(session: Session, package_pk: int) -> RulePackage:
    model = session.get(RulePackageModel, package_pk)
    if model is None:
        raise ValueError("Ruleset inexistente")
    parameters = {item.parameter_id: item.value for item in session.scalars(
        select(ParameterModel).where(ParameterModel.package_id == model.id)
    )}
    rules: list[Rule] = []
    exercise_ids: set[str] = set()
    evidence_ids: set[str] = set()
    for item in session.scalars(select(RuleModel).where(RuleModel.package_id == model.id).order_by(RuleModel.rule_id)):
        condition = session.scalar(select(RuleConditionModel).where(RuleConditionModel.rule_id == item.id))
        actions = []
        for action in session.scalars(select(RuleActionModel).where(RuleActionModel.rule_id == item.id).order_by(RuleActionModel.id)):
            actions.append(Action(ActionType(action.action_type), action.target, action.value, action.parameter_id))
            if action.action_type in {"INCLUDE_EXERCISE", "EXCLUDE_EXERCISE"}:
                exercise_ids.add(action.target)
        for source_id in session.scalars(
            select(EvidenceModel.source_id).join(RuleEvidenceModel, RuleEvidenceModel.evidence_id == EvidenceModel.id)
            .where(RuleEvidenceModel.rule_id == item.id)
        ):
            evidence_ids.add(source_id)
        rules.append(Rule(
            rule_id=item.rule_id, rule_type=RuleType(item.rule_type), priority=item.priority,
            condition=_condition_from_payload(condition.payload), actions=tuple(actions),
            rationale=item.rationale, classification=item.classification, evidence_status=item.evidence_status,
        ))
    return RulePackage(
        package_id=model.package_id, version=model.version, status=model.status,
        schema_version=model.schema_version, parameters=parameters,
        exercises=frozenset(exercise_ids), evidence=frozenset(evidence_ids),
        rules=tuple(rules), manifest=model.manifest,
    )


def importar_ruleset(session: Session, root: Path) -> RulePackageModel:
    """Valida completamente antes de añadir objetos a la transacción actual."""
    errors = validate_rule_package(root)
    if errors:
        raise ValueError("Paquete inválido: " + "; ".join(errors))
    manifest = _read(root, "manifest.json")
    existing = session.scalar(select(RulePackageModel).where(
        RulePackageModel.package_id == manifest["package_id"],
        RulePackageModel.version == manifest["version"],
    ))
    if existing:
        raise ValueError("La versión ya fue importada y es inmutable")
    if manifest["status"] == "ACTIVE" and session.scalar(select(RulePackageModel).where(RulePackageModel.status == "ACTIVE")):
        raise ValueError("Ya existe un ruleset ACTIVE")

    package = RulePackageModel(
        package_id=manifest["package_id"], version=manifest["version"],
        status=manifest["status"], schema_version=manifest["schema_version"], manifest=manifest,
    )
    session.add(package); session.flush()
    parameter_ids: dict[str, ParameterModel] = {}
    for item in _read(root, "parameters.json"):
        model = ParameterModel(
            package_id=package.id, parameter_id=item["parameter_id"],
            category=item["category"], value=item["value"], unit=item.get("unit"),
        )
        session.add(model); parameter_ids[item["parameter_id"]] = model
    for item in _read(root, "exercises.json"):
        current = session.scalar(select(ExerciseModel).where(ExerciseModel.exercise_id == item["exercise_id"]))
        if current is None:
            session.add(ExerciseModel(
                exercise_id=item["exercise_id"], name=item["name"], category=item["category"],
                objective=item["objective"], equipment=item.get("equipment", []),
                contraindications=item.get("contraindications", []), prescription=item,
            ))
    sources: dict[str, EvidenceModel] = {}
    for item in _read(root, "evidence.json"):
        current = session.scalar(select(EvidenceModel).where(EvidenceModel.source_id == item["source_id"]))
        if current is None:
            current = EvidenceModel(
                source_id=item["source_id"], source_type=item["source_type"], authors=item["authors"],
                title=item["title"], year=item["year"], journal=item.get("journal"),
                volume=item.get("volume"), issue=item.get("issue"), pages=item.get("pages"),
                doi=item.get("doi"), pmid=item.get("pmid"), url=item["url"],
                accessed_date=date.fromisoformat(item["accessed_date"]),
                evidence_level=item["evidence_level"], climbing_specific=item["climbing_specific"],
                population=item.get("population"), main_finding=item["main_finding"],
                limitations=item["limitations"], notes=item.get("notes"),
            )
            session.add(current); session.flush()
        sources[item["source_id"]] = current
    rules: dict[str, RuleModel] = {}
    for item in _read(root, "rules.json"):
        rule = RuleModel(
            package_id=package.id, rule_id=item["rule_id"], rule_type=item["rule_type"],
            priority=item["priority"], rationale=item["rationale"],
            classification=item["classification"], evidence_status=item["evidence_status"],
        )
        session.add(rule); session.flush(); rules[item["rule_id"]] = rule
        session.add(RuleConditionModel(rule_id=rule.id, payload=item["condition"]))
        for action in item["actions"]:
            session.add(RuleActionModel(
                rule_id=rule.id, action_type=action["action_type"], target=action["target"],
                value=action.get("value"), parameter_id=action.get("parameter_id"),
            ))
    for item in _read(root, "rule_evidence.json"):
        session.add(RuleEvidenceModel(
            rule_id=rules[item["rule_id"]].id, evidence_id=sources[item["source_id"]].id,
            relation_type=item["relation_type"], strength=item["evidence_strength"], notes=item.get("notes"),
        ))
    session.flush()
    return package


def importar_ruleset_zip(session: Session, archive_path: Path) -> RulePackageModel:
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        names = {item.filename for item in members}
        if names != REQUIRED_FILES:
            raise ValueError("El ZIP debe contener únicamente los seis archivos canónicos")
        if sum(item.file_size for item in members) > MAX_PACKAGE_BYTES:
            raise ValueError("El paquete supera el límite de 10 MiB")
        if any(PurePosixPath(item.filename).name != item.filename for item in members):
            raise ValueError("El paquete contiene rutas no permitidas")
        with tempfile.TemporaryDirectory(prefix="climber-rules-") as temporary:
            root = Path(temporary)
            for item in members:
                root.joinpath(item.filename).write_bytes(archive.read(item))
            # Los esquemas son recursos de la aplicación, no contenido confiable del ZIP.
            return importar_ruleset(session, root)


def activar_ruleset(session: Session, package_id: int) -> RulePackageModel:
    package = session.get(RulePackageModel, package_id)
    if package is None:
        raise ValueError("Ruleset inexistente")
    if package.status not in {"TESTING", "ACTIVE"}:
        raise ValueError("Solo un ruleset validado en TESTING puede activarse")
    session.query(RulePackageModel).filter(
        RulePackageModel.status == "ACTIVE", RulePackageModel.id != package.id,
    ).update({RulePackageModel.status: "DEPRECATED"}, synchronize_session=False)
    package.status = "ACTIVE"
    session.flush()
    return package
