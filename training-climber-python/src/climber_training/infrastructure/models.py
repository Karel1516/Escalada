from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    alias: Mapped[str] = mapped_column(String(120), unique=True)
    age: Mapped[int | None]
    sex: Mapped[str | None] = mapped_column(String(30))
    weight_kg: Mapped[float | None]
    height_cm: Mapped[float | None]
    ape_index_cm: Mapped[float | None]
    experience_years: Mapped[float] = mapped_column(default=0)
    level: Mapped[str] = mapped_column(String(30), default="principiante")
    modality: Mapped[str] = mapped_column(String(30), default="mixto")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class AvailabilityModel(Base):
    __tablename__ = "user_availability"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    weekdays: Mapped[list[int]] = mapped_column(JSON)
    max_session_minutes: Mapped[int]
    min_rest_hours: Mapped[int]
    locations: Mapped[list[str]] = mapped_column(JSON)
    time_restrictions: Mapped[dict[str, Any]] = mapped_column(JSON)


class GradeRecordModel(Base):
    __tablename__ = "user_grades"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    discipline: Mapped[str] = mapped_column(String(30))
    grade_scale: Mapped[str] = mapped_column(String(40))
    usual_grade: Mapped[str | None] = mapped_column(String(20))
    max_worked: Mapped[str | None] = mapped_column(String(20))
    max_sent: Mapped[str | None] = mapped_column(String(20))
    recorded_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class EquipmentModel(Base):
    __tablename__ = "user_equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    equipment_code: Mapped[str] = mapped_column(String(80))
    available: Mapped[bool] = mapped_column(default=True)
    __table_args__ = (UniqueConstraint("user_id", "equipment_code"),)


class LimitationModel(Base):
    __tablename__ = "user_limitations"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    region: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)


class ObjectiveModel(Base):
    __tablename__ = "objectives"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    priority: Mapped[int] = mapped_column(default=1)
    primary: Mapped[bool] = mapped_column(default=False)


class RulePackageModel(Base):
    __tablename__ = "rule_packages"
    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[str] = mapped_column(String(100))
    version: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(30), index=True)
    schema_version: Mapped[str] = mapped_column(String(30))
    manifest: Mapped[dict[str, Any]] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint("package_id", "version"),)


class RuleModel(Base):
    __tablename__ = "rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("rule_packages.id", ondelete="RESTRICT"), index=True)
    rule_id: Mapped[str] = mapped_column(String(100))
    rule_type: Mapped[str] = mapped_column(String(40))
    priority: Mapped[int]
    rationale: Mapped[str] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String(40))
    evidence_status: Mapped[str] = mapped_column(String(30))
    __table_args__ = (UniqueConstraint("package_id", "rule_id"),)


class RuleConditionModel(Base):
    __tablename__ = "rule_conditions"
    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class RuleActionModel(Base):
    __tablename__ = "rule_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"), index=True)
    action_type: Mapped[str] = mapped_column(String(50))
    target: Mapped[str] = mapped_column(String(120))
    value: Mapped[Any | None] = mapped_column(JSON)
    parameter_id: Mapped[str | None] = mapped_column(String(100))


class ParameterModel(Base):
    __tablename__ = "parameters"
    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("rule_packages.id", ondelete="RESTRICT"), index=True)
    parameter_id: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(60))
    value: Mapped[Any] = mapped_column(JSON)
    unit: Mapped[str | None] = mapped_column(String(30))
    __table_args__ = (UniqueConstraint("package_id", "parameter_id"),)


class RuleParameterModel(Base):
    __tablename__ = "rule_parameters"
    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"))
    parameter_id: Mapped[int] = mapped_column(ForeignKey("parameters.id", ondelete="RESTRICT"))
    __table_args__ = (UniqueConstraint("rule_id", "parameter_id"),)


class EvidenceModel(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(100), unique=True)
    source_type: Mapped[str] = mapped_column(String(50))
    authors: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    year: Mapped[int]
    journal: Mapped[str | None] = mapped_column(String(200))
    volume: Mapped[str | None] = mapped_column(String(40))
    issue: Mapped[str | None] = mapped_column(String(40))
    pages: Mapped[str | None] = mapped_column(String(60))
    doi: Mapped[str | None] = mapped_column(String(160), unique=True)
    pmid: Mapped[str | None] = mapped_column(String(30), unique=True)
    url: Mapped[str]
    accessed_date: Mapped[date]
    evidence_level: Mapped[str]
    climbing_specific: Mapped[bool]
    population: Mapped[str | None] = mapped_column(Text)
    main_finding: Mapped[str] = mapped_column(Text)
    limitations: Mapped[str] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)


class RuleEvidenceModel(Base):
    __tablename__ = "rule_evidence"
    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id", ondelete="CASCADE"))
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id", ondelete="RESTRICT"))
    relation_type: Mapped[str] = mapped_column(String(40))
    strength: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("rule_id", "evidence_id", "relation_type"),)


class ExerciseModel(Base):
    __tablename__ = "exercises"
    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80), index=True)
    objective: Mapped[str] = mapped_column(String(80))
    equipment: Mapped[list[str]] = mapped_column(JSON)
    contraindications: Mapped[list[str]] = mapped_column(JSON)
    prescription: Mapped[dict[str, Any]] = mapped_column(JSON)


class TestModel(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    test_id: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    protocol: Mapped[str] = mapped_column(Text)
    eligibility: Mapped[dict[str, Any]] = mapped_column(JSON)
    source_id: Mapped[str | None] = mapped_column(String(100))


class PlanModel(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    package_version: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    rules_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class SessionModel(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="RESTRICT"), index=True)
    scheduled_date: Mapped[date]
    objective: Mapped[str]
    duration_minutes: Mapped[int]


class SessionExerciseModel(Base):
    __tablename__ = "session_exercises"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="RESTRICT"), index=True)
    exercise_id: Mapped[str] = mapped_column(String(100))
    prescription: Mapped[dict[str, Any]] = mapped_column(JSON)
    rule_ids: Mapped[list[str]] = mapped_column(JSON)


class SessionFeedbackModel(Base):
    __tablename__ = "session_feedback"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="RESTRICT"), unique=True)
    completion: Mapped[str]
    completion_percent: Mapped[int]
    rpe: Mapped[float | None]
    fatigue: Mapped[float | None]
    pain: Mapped[float | None]
    details: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class TestHistoryModel(Base):
    __tablename__ = "test_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    test_id: Mapped[str] = mapped_column(String(100))
    performed_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    result: Mapped[float]
    unit: Mapped[str]
    protocol: Mapped[str]
    package_version: Mapped[str]
    notes: Mapped[str | None] = mapped_column(Text)


class DecisionLogModel(Base):
    __tablename__ = "decision_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id", ondelete="RESTRICT"), index=True)
    package_version: Mapped[str]
    rule_id: Mapped[str] = mapped_column(String(100), index=True)
    input_values: Mapped[dict[str, Any]] = mapped_column(JSON)
    action: Mapped[str]
    previous_value: Mapped[Any | None] = mapped_column(JSON)
    new_value: Mapped[Any | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class GradeScaleModel(Base):
    __tablename__ = "grade_scales"
    id: Mapped[int] = mapped_column(primary_key=True)
    scale: Mapped[str] = mapped_column(String(40))
    discipline: Mapped[str] = mapped_column(String(30))
    label: Mapped[str] = mapped_column(String(20))
    ordinal: Mapped[int]
    __table_args__ = (UniqueConstraint("scale", "discipline", "label"),)
