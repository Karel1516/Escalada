from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .enums import ActionType, Operator, RuleType


@dataclass(frozen=True)
class Condition:
    field: str
    operator: Operator
    value: Any = None


@dataclass(frozen=True)
class ConditionGroup:
    combinator: str
    conditions: tuple[Condition | "ConditionGroup", ...]


@dataclass(frozen=True)
class Action:
    action_type: ActionType
    target: str
    value: Any = None
    parameter_id: str | None = None


@dataclass(frozen=True)
class Rule:
    rule_id: str
    rule_type: RuleType
    priority: int
    condition: Condition | ConditionGroup
    actions: tuple[Action, ...]
    rationale: str
    classification: str
    evidence_status: str


@dataclass(frozen=True)
class RulePackage:
    package_id: str
    version: str
    status: str
    schema_version: str
    parameters: dict[str, Any]
    exercises: frozenset[str]
    evidence: frozenset[str]
    rules: tuple[Rule, ...]
    manifest: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    rule_id: str
    rule_type: RuleType
    action: ActionType
    target: str
    previous_value: Any
    new_value: Any
    package_version: str
    input_values: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class EvaluationResult:
    values: dict[str, Any] = field(default_factory=dict)
    included_exercises: set[str] = field(default_factory=set)
    excluded_exercises: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    debug: list[dict[str, Any]] = field(default_factory=list)
