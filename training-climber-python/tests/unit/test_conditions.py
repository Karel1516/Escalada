import pytest

from climber_training.domain.entities import Condition, ConditionGroup
from climber_training.domain.enums import Operator
from climber_training.rule_engine.evaluator import evaluar_condicion


@pytest.mark.parametrize(("operator", "actual", "expected", "answer"), [
    (Operator.EQ, 3, 3, True), (Operator.NEQ, 3, 4, True),
    (Operator.GT, 4, 3, True), (Operator.GTE, 3, 3, True),
    (Operator.LT, 2, 3, True), (Operator.LTE, 3, 3, True),
    (Operator.BETWEEN, 3, [2, 4], True), (Operator.IN, "a", ["a", "b"], True),
    (Operator.NOT_IN, "z", ["a", "b"], True),
])
def test_operators(operator, actual, expected, answer):
    assert evaluar_condicion(Condition("value", operator, expected), {"value": actual}) is answer


def test_exists_nested_and_or():
    context = {"profile": {"age": 30}}
    group = ConditionGroup("AND", (
        Condition("profile.age", Operator.EXISTS),
        ConditionGroup("OR", (Condition("profile.age", Operator.LT, 10), Condition("profile.age", Operator.GT, 20))),
    ))
    assert evaluar_condicion(group, context)
    assert evaluar_condicion(Condition("missing", Operator.NOT_EXISTS), context)
