from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from climber_training.infrastructure.models import (
    AvailabilityModel, DecisionLogModel, EquipmentModel, LimitationModel,
    ObjectiveModel, PlanModel, SessionExerciseModel, SessionFeedbackModel,
    SessionModel, TestHistoryModel, UserModel,
)
from climber_training.domain.entities import RulePackage
from climber_training.rule_engine import RuleEngine, cargar_rule_package


def validar_perfil(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not str(data.get("alias", "")).strip():
        errors["alias"] = "El alias es obligatorio."
    age = data.get("age")
    if age is not None and not 10 <= int(age) <= 100:
        errors["age"] = "La edad debe estar entre 10 y 100."
    if float(data.get("experience_years", 0)) < 0:
        errors["experience_years"] = "La experiencia no puede ser negativa."
    return errors


def guardar_perfil(session: Session, data: dict[str, Any]) -> UserModel:
    errors = validar_perfil(data)
    if errors:
        raise ValueError(errors)
    user = UserModel(**data)
    session.add(user)
    session.flush()
    return user


def actualizar_perfil(session: Session, user_id: int, data: dict[str, Any]) -> UserModel:
    errors = validar_perfil(data)
    if errors:
        raise ValueError(errors)
    user = session.get(UserModel, user_id)
    if user is None:
        raise ValueError("Usuario inexistente")
    for key, value in data.items():
        setattr(user, key, value)
    session.flush()
    return user


def guardar_contexto_usuario(
    session: Session, user_id: int, *, objective: str, weekdays: list[int],
    max_minutes: int, equipment: dict[str, bool], limitations: dict[str, str],
) -> None:
    if not weekdays:
        raise ValueError("Selecciona al menos un día disponible")
    if not 20 <= max_minutes <= 300:
        raise ValueError("La sesión debe durar entre 20 y 300 minutos")
    for model in (AvailabilityModel, EquipmentModel, LimitationModel, ObjectiveModel):
        session.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
    session.add(AvailabilityModel(
        user_id=user_id, weekdays=sorted(set(weekdays)), max_session_minutes=max_minutes,
        min_rest_hours=24, locations=[], time_restrictions={},
    ))
    session.add(ObjectiveModel(user_id=user_id, code=objective, priority=1, primary=True))
    session.add_all(EquipmentModel(user_id=user_id, equipment_code=code, available=value) for code, value in equipment.items())
    session.add_all(LimitationModel(user_id=user_id, region=region, status=status) for region, status in limitations.items())
    session.flush()


def cargar_contexto_usuario(session: Session, user_id: int) -> dict[str, Any]:
    user = session.get(UserModel, user_id)
    if user is None:
        raise ValueError("Usuario inexistente")
    availability = session.scalar(select(AvailabilityModel).where(AvailabilityModel.user_id == user_id))
    objective = session.scalar(select(ObjectiveModel).where(ObjectiveModel.user_id == user_id, ObjectiveModel.primary.is_(True)))
    equipment = {item.equipment_code: item.available for item in session.scalars(select(EquipmentModel).where(EquipmentModel.user_id == user_id))}
    limitations = {item.region: item.status for item in session.scalars(select(LimitationModel).where(LimitationModel.user_id == user_id))}
    latest_feedback = session.scalar(
        select(SessionFeedbackModel)
        .join(SessionModel, SessionFeedbackModel.session_id == SessionModel.id)
        .join(PlanModel, SessionModel.plan_id == PlanModel.id)
        .where(PlanModel.user_id == user_id)
        .order_by(SessionFeedbackModel.created_at.desc(), SessionFeedbackModel.id.desc())
        .limit(1)
    )
    context = {
        "age": user.age, "level": user.level, "modality": user.modality,
        "experience_years": user.experience_years,
        "objective": objective.code if objective else "acondicionamiento_general",
        "equipment": equipment,
        "limitations": limitations,
        "availability": {
            "days": availability.weekdays if availability else [0, 3],
            "max_minutes": availability.max_session_minutes if availability else 60,
        },
    }
    if latest_feedback:
        context["feedback"] = {
            "completion": latest_feedback.completion,
            "completion_percent": latest_feedback.completion_percent,
            "rpe": latest_feedback.rpe,
            "fatigue": latest_feedback.fatigue,
            "pain": latest_feedback.pain,
        }
    return context


def generar_plan(
    session: Session, *, user_id: int, package_path: Path | None = None,
    package: RulePackage | None = None,
    context: dict[str, Any], start_date: date | None = None,
) -> PlanModel:
    if package is None:
        if package_path is None:
            raise ValueError("Falta seleccionar un ruleset")
        package = cargar_rule_package(package_path)
    if package.status == "RESEARCH":
        raise ValueError("Un ruleset RESEARCH no puede generar planes de usuario")
    result = RuleEngine().evaluar_reglas(package, context, debug=True)
    plan = PlanModel(
        user_id=user_id, package_version=package.version,
        input_snapshot=context,
        rules_snapshot={
            "package_id": package.package_id, "version": package.version,
            "decisions": [asdict(d) for d in result.decisions],
        },
    )
    session.add(plan); session.flush()
    for decision in result.decisions:
        session.add(DecisionLogModel(
            user_id=user_id, plan_id=plan.id, package_version=package.version,
            rule_id=decision.rule_id, input_values=decision.input_values,
            action=decision.action.value, previous_value=decision.previous_value,
            new_value=decision.new_value,
        ))
    generar_semana(session, plan, result, context, start_date or date.today())
    return plan


def generar_semana(session: Session, plan: PlanModel, result, context: dict[str, Any], start: date) -> list[SessionModel]:
    available_days = context.get("availability", {}).get("days", [0, 3])
    max_minutes = int(context.get("availability", {}).get("max_minutes", 60))
    selected = sorted(result.included_exercises - result.excluded_exercises)
    sessions: list[SessionModel] = []
    for weekday in available_days:
        offset = (int(weekday) - start.weekday()) % 7
        item = SessionModel(
            plan_id=plan.id, scheduled_date=start + timedelta(days=offset),
            objective=context.get("objective", "acondicionamiento_general"),
            duration_minutes=min(max_minutes, 60),
        )
        session.add(item); session.flush(); sessions.append(item)
        for exercise in selected:
            rule_ids = [d.rule_id for d in result.decisions if d.target == exercise]
            session.add(SessionExerciseModel(
                session_id=item.id, exercise_id=exercise,
                prescription=result.values, rule_ids=sorted(set(rule_ids)),
            ))
    return sessions


def registrar_sesion(session: Session, session_id: int, feedback: dict[str, Any]) -> SessionFeedbackModel:
    item = SessionFeedbackModel(session_id=session_id, **feedback)
    session.add(item); session.flush()
    return item


def ejecutar_reevaluacion(session: Session, user_id: int, test_id: str, result: float, unit: str, protocol: str, package_version: str, notes: str = "") -> TestHistoryModel:
    item = TestHistoryModel(user_id=user_id, test_id=test_id, result=result, unit=unit, protocol=protocol, package_version=package_version, notes=notes)
    session.add(item); session.flush()
    return item


def crear_nuevo_ciclo(session: Session, **kwargs) -> PlanModel:
    return generar_plan(session, **kwargs)


def actualizar_progresion(feedback: dict[str, Any]) -> dict[str, Any]:
    """Devuelve contexto; la decisión PROGRESS/MAINTAIN/etc. pertenece al ruleset."""
    return {"feedback": feedback}


def mostrar_trazabilidad(session: Session, plan_id: int) -> list[DecisionLogModel]:
    return list(session.query(DecisionLogModel).filter_by(plan_id=plan_id).order_by(DecisionLogModel.id))


def listar_usuarios(session: Session) -> list[UserModel]:
    return list(session.scalars(select(UserModel).where(UserModel.active.is_(True)).order_by(UserModel.alias)))


def listar_sesiones(session: Session, plan_id: int) -> list[SessionModel]:
    return list(session.scalars(select(SessionModel).where(SessionModel.plan_id == plan_id).order_by(SessionModel.scheduled_date)))


def ultimo_plan(session: Session, user_id: int) -> PlanModel | None:
    return session.scalar(select(PlanModel).where(PlanModel.user_id == user_id).order_by(PlanModel.created_at.desc(), PlanModel.id.desc()).limit(1))
