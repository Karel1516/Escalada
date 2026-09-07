from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from climber_training.domain.entities import Condition, ConditionGroup
from climber_training.domain.enums import Operator


def resolve_path(context: Mapping[str, Any], path: str) -> tuple[bool, Any]:
    current: Any = context
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return False, None
        current = current[part]
    return True, current


def evaluar_condicion(condition: Condition | ConditionGroup, context: Mapping[str, Any]) -> bool:
    if isinstance(condition, ConditionGroup):
        results = [evaluar_condicion(child, context) for child in condition.conditions]
        return all(results) if condition.combinator == "AND" else any(results)

    exists, actual = resolve_path(context, condition.field)
    expected = condition.value
    op = condition.operator
    if op == Operator.EXISTS:
        return exists and actual is not None
    if op == Operator.NOT_EXISTS:
        return not exists or actual is None
    if not exists:
        return False
    operations = {
        Operator.EQ: lambda: actual == expected,
        Operator.NEQ: lambda: actual != expected,
        Operator.GT: lambda: actual > expected,
        Operator.GTE: lambda: actual >= expected,
        Operator.LT: lambda: actual < expected,
        Operator.LTE: lambda: actual <= expected,
        Operator.BETWEEN: lambda: expected[0] <= actual <= expected[1],
        Operator.IN: lambda: actual in expected,
        Operator.NOT_IN: lambda: actual not in expected,
    }
    try:
        return operations[op]()
    except (KeyError, TypeError, IndexError):
        return False
