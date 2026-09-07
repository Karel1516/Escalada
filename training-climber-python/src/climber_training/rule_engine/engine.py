from __future__ import annotations

from dataclasses import replace
from typing import Any

from climber_training.domain.entities import Action, Decision, EvaluationResult, Rule, RulePackage
from climber_training.domain.enums import ActionType, PRECEDENCE, RuleType

from .evaluator import evaluar_condicion


MUTATING_ACTIONS = {
    ActionType.SET_SETS, ActionType.SET_REPS, ActionType.SET_DURATION,
    ActionType.SET_INTENSITY, ActionType.SET_REST, ActionType.SET_MIN,
    ActionType.SET_MAX, ActionType.SET_FREQUENCY, ActionType.SET_LOAD,
    ActionType.SET_LOAD_PERCENT, ActionType.SET_RPE, ActionType.SET_RIR,
    ActionType.ALLOW_PROGRESSION, ActionType.BLOCK_PROGRESSION,
}


class RuleEngine:
    """Evaluador determinista. El catálogo controla toda operación permitida."""

    def evaluar_reglas(
        self, package: RulePackage, context: dict[str, Any], *, debug: bool = False
    ) -> EvaluationResult:
        result = EvaluationResult()
        winning: dict[tuple[str, str], tuple[tuple[int, int, str], Rule, Action]] = {}
        ordered = sorted(package.rules, key=self._rank, reverse=True)
        for rule in ordered:
            matched = evaluar_condicion(rule.condition, context)
            if debug:
                result.debug.append({"rule_id": rule.rule_id, "matched": matched})
            if not matched:
                continue
            for action in rule.actions:
                resolved = self._resolve_parameter(action, package.parameters)
                key = self._conflict_key(resolved)
                rank = self._rank(rule)
                if key in winning:
                    winner_rank, winner_rule, winner_action = winning[key]
                    result.conflicts.append({
                        "target": key, "winner": winner_rule.rule_id,
                        "loser": rule.rule_id, "winning_action": winner_action.action_type.value,
                    })
                    if rank <= winner_rank:
                        continue
                winning[key] = (rank, rule, resolved)

        for _, rule, action in sorted(winning.values(), key=lambda item: item[0]):
            self.ejecutar_accion(action, rule, package, context, result)
        return result

    @staticmethod
    def _rank(rule: Rule) -> tuple[int, int, str]:
        precedence = PRECEDENCE.get(rule.rule_type, 200)
        return precedence, rule.priority, rule.rule_id

    @staticmethod
    def _conflict_key(action: Action) -> tuple[str, str]:
        if action.action_type in {ActionType.INCLUDE_EXERCISE, ActionType.EXCLUDE_EXERCISE}:
            return "exercise-membership", action.target
        if action.action_type in {ActionType.ALLOW_PROGRESSION, ActionType.BLOCK_PROGRESSION}:
            return "progression", action.target
        return action.action_type.value, action.target

    @staticmethod
    def _resolve_parameter(action: Action, parameters: dict[str, Any]) -> Action:
        if action.parameter_id:
            return replace(action, value=parameters[action.parameter_id])
        return action

    def ejecutar_accion(
        self, action: Action, rule: Rule, package: RulePackage,
        context: dict[str, Any], result: EvaluationResult,
    ) -> None:
        old: Any = None
        new = action.value
        if action.action_type == ActionType.INCLUDE_EXERCISE:
            old = action.target in result.included_exercises
            result.included_exercises.add(action.target)
            result.excluded_exercises.discard(action.target)
            new = True
        elif action.action_type == ActionType.EXCLUDE_EXERCISE:
            old = action.target in result.excluded_exercises
            result.excluded_exercises.add(action.target)
            result.included_exercises.discard(action.target)
            new = True
        elif action.action_type == ActionType.SHOW_WARNING:
            result.warnings.append(str(action.value))
        elif action.action_type == ActionType.MULTIPLY_VOLUME:
            old = result.values.get(action.target, 1)
            new = old * action.value
            result.values[action.target] = new
        elif action.action_type in MUTATING_ACTIONS:
            old = result.values.get(action.target)
            new = action.value if action.value is not None else True
            result.values[action.target] = new
        elif action.action_type in {ActionType.TRIGGER_DELOAD, ActionType.TRIGGER_REEVALUATION}:
            old = result.values.get(action.target)
            new = True
            result.values[action.target] = True
        elif action.action_type in {ActionType.INCLUDE_CATEGORY, ActionType.EXCLUDE_CATEGORY}:
            old = result.values.get(action.target)
            new = action.action_type.value
            result.values[action.target] = new
        else:  # pragma: no cover - enums and validation make this defensive only
            raise ValueError(f"Unsupported action: {action.action_type}")
        result.decisions.append(Decision(
            rule_id=rule.rule_id, rule_type=rule.rule_type, action=action.action_type,
            target=action.target, previous_value=old, new_value=new,
            package_version=package.version, input_values=dict(context),
        ))


def evaluar_reglas(package: RulePackage, context: dict[str, Any], debug: bool = False) -> EvaluationResult:
    return RuleEngine().evaluar_reglas(package, context, debug=debug)
