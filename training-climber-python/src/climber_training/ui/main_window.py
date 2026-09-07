from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton, QSpinBox,
    QStackedWidget, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget,
)
from sqlalchemy import select

from climber_training.application.reporting import exportar_plan_pdf
from climber_training.application.services import (
    cargar_contexto_usuario, ejecutar_reevaluacion, generar_plan, guardar_contexto_usuario,
    guardar_perfil, listar_sesiones, listar_usuarios, registrar_sesion, ultimo_plan,
)
from climber_training.infrastructure.backup import export_backup, restore_backup
from climber_training.infrastructure.config import Settings
from climber_training.infrastructure.models import (
    DecisionLogModel, PlanModel, RulePackageModel, SessionFeedbackModel, TestHistoryModel, TestModel,
)
from climber_training.infrastructure.rulesets import cargar_rule_package_db, importar_ruleset_zip
from climber_training.rule_engine import validate_rule_package

PAGES = [
    "Inicio / Dashboard", "Perfil", "Contexto y objetivos", "Plan",
    "Registrar entrenamiento", "Historial y trazabilidad", "Configuración",
    "Modo técnico / Debug", "Evaluaciones", "Sesión actual", "Progreso",
    "Equipo avanzado", "Catálogos técnicos",
]
WEEKDAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


class MainWindow(QMainWindow):
    def __init__(self, package_version: str = "demo", session_factory=None, package_path: Path | None = None) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.package_path = package_path
        self.current_user_id: int | None = None
        self.current_plan_id: int | None = None
        self.setWindowTitle("Entrenamiento Escalada")
        self.resize(1100, 720)
        shell = QWidget(); outer = QVBoxLayout(shell)
        title = QLabel("Entrenamiento Escalada")
        title.setStyleSheet("font-size: 24px; font-weight: 600; padding: 8px")
        outer.addWidget(title)
        body = QHBoxLayout(); outer.addLayout(body)
        self.navigation = QListWidget(); self.navigation.addItems(PAGES)
        self.navigation.setFixedWidth(220); body.addWidget(self.navigation)
        self.pages = QStackedWidget(); body.addWidget(self.pages, 1)
        self._build_dashboard(package_version); self._build_profile(); self._build_context()
        self._build_plan(); self._build_feedback(); self._build_history()
        self._build_settings(); self._build_debug()
        self._build_evaluations()
        for name in PAGES[9:]: self._build_placeholder(name)
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0); self.setCentralWidget(shell)
        self.refresh_users(); self.refresh_rulesets(); self.refresh_tests()

    @staticmethod
    def _page(title: str) -> tuple[QWidget, QVBoxLayout]:
        widget = QWidget(); layout = QVBoxLayout(widget)
        heading = QLabel(title); heading.setStyleSheet("font-size: 20px; font-weight: 600")
        layout.addWidget(heading)
        return widget, layout

    def _build_dashboard(self, package_version: str) -> None:
        page, layout = self._page(PAGES[0]); layout.addWidget(QLabel(f"Recursos incluidos: {package_version}"))
        row = QHBoxLayout(); row.addWidget(QLabel("Usuario activo:")); self.user_combo = QComboBox()
        self.user_combo.currentIndexChanged.connect(self._user_changed); row.addWidget(self.user_combo, 1); layout.addLayout(row)
        rules_row = QHBoxLayout(); rules_row.addWidget(QLabel("Ruleset:")); self.ruleset_combo = QComboBox()
        rules_row.addWidget(self.ruleset_combo, 1); layout.addLayout(rules_row)
        self.dashboard_status = QLabel("Crea un perfil para comenzar."); self.dashboard_status.setWordWrap(True); layout.addWidget(self.dashboard_status)
        create = QPushButton("Nuevo usuario"); create.clicked.connect(lambda: self.navigation.setCurrentRow(1))
        generate = QPushButton("Generar plan auditable"); generate.clicked.connect(self.generate_current_plan)
        layout.addWidget(create); layout.addWidget(generate); layout.addStretch(); self.pages.addWidget(page)

    def _build_profile(self) -> None:
        page, layout = self._page(PAGES[1]); form = QFormLayout()
        self.alias = QLineEdit(); self.age = QSpinBox(); self.age.setRange(10, 100); self.age.setValue(25)
        self.experience = QSpinBox(); self.experience.setRange(0, 80)
        self.level = QComboBox(); self.level.addItems(["principiante", "intermedio", "avanzado", "elite"])
        self.modality = QComboBox(); self.modality.addItems(["boulder", "deportiva", "mixto"])
        form.addRow("Alias*", self.alias); form.addRow("Edad", self.age); form.addRow("Años escalando", self.experience)
        form.addRow("Nivel", self.level); form.addRow("Modalidad", self.modality); layout.addLayout(form)
        save = QPushButton("Guardar nuevo perfil"); save.clicked.connect(self.save_profile); layout.addWidget(save)
        self.profile_message = QLabel(); self.profile_message.setWordWrap(True); layout.addWidget(self.profile_message)
        layout.addStretch(); self.pages.addWidget(page)

    def _build_context(self) -> None:
        page, layout = self._page(PAGES[2]); form = QFormLayout()
        self.objective = QComboBox(); self.objective.addItems([
            "acondicionamiento_general", "finger_strength", "fuerza_maxima", "potencia",
            "resistencia", "power_endurance", "tecnica", "retorno_progresivo",
        ])
        self.max_minutes = QSpinBox(); self.max_minutes.setRange(20, 300); self.max_minutes.setValue(60)
        form.addRow("Objetivo principal", self.objective); form.addRow("Máximo por sesión (min)", self.max_minutes); layout.addLayout(form)
        layout.addWidget(QLabel("Días disponibles")); days = QHBoxLayout(); self.day_checks = []
        for label in WEEKDAYS:
            item = QCheckBox(label); self.day_checks.append(item); days.addWidget(item)
        self.day_checks[0].setChecked(True); self.day_checks[3].setChecked(True); layout.addLayout(days)
        self.wall = QCheckBox("Muro disponible"); self.hangboard = QCheckBox("Hangboard disponible")
        layout.addWidget(self.wall); layout.addWidget(self.hangboard)
        self.finger_limitation = QComboBox(); self.finger_limitation.addItems(["ninguna", "leve", "limitacion", "lesion_rehabilitacion"])
        limit_form = QFormLayout(); limit_form.addRow("Estado de dedos", self.finger_limitation); layout.addLayout(limit_form)
        save = QPushButton("Guardar contexto"); save.clicked.connect(self.save_context); layout.addWidget(save)
        self.context_message = QLabel(); self.context_message.setWordWrap(True); layout.addWidget(self.context_message)
        layout.addStretch(); self.pages.addWidget(page)

    def _build_plan(self) -> None:
        page, layout = self._page(PAGES[3]); self.plan_summary = QLabel("Sin plan generado.")
        self.plan_summary.setWordWrap(True); layout.addWidget(self.plan_summary)
        self.plan_table = QTableWidget(0, 3); self.plan_table.setHorizontalHeaderLabels(["Fecha", "Objetivo", "Minutos"])
        self.plan_table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.plan_table)
        export = QPushButton("Exportar plan PDF"); export.clicked.connect(self.export_plan); layout.addWidget(export)
        self.pages.addWidget(page)

    def _build_feedback(self) -> None:
        page, layout = self._page(PAGES[4]); form = QFormLayout()
        self.session_combo = QComboBox(); self.completion = QComboBox(); self.completion.addItems(["completada", "parcial", "omitida"])
        self.completion_percent = QSpinBox(); self.completion_percent.setRange(0, 100); self.completion_percent.setValue(100)
        self.rpe = QSpinBox(); self.rpe.setRange(0, 10); self.fatigue = QSpinBox(); self.fatigue.setRange(0, 10)
        self.pain = QSpinBox(); self.pain.setRange(0, 10); self.feedback_notes = QTextEdit(); self.feedback_notes.setMaximumHeight(100)
        form.addRow("Sesión", self.session_combo); form.addRow("Estado", self.completion); form.addRow("Completado %", self.completion_percent)
        form.addRow("RPE", self.rpe); form.addRow("Fatiga", self.fatigue); form.addRow("Dolor", self.pain); form.addRow("Comentarios", self.feedback_notes)
        layout.addLayout(form); save = QPushButton("Registrar sin sobrescribir"); save.clicked.connect(self.save_feedback)
        layout.addWidget(save); self.feedback_message = QLabel(); layout.addWidget(self.feedback_message); layout.addStretch(); self.pages.addWidget(page)

    def _build_history(self) -> None:
        page, layout = self._page(PAGES[5]); self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["RuleID", "Acción", "Objetivo", "Anterior", "Nuevo"])
        self.history_table.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.history_table)
        refresh = QPushButton("Actualizar trazabilidad"); refresh.clicked.connect(self.refresh_history); layout.addWidget(refresh); self.pages.addWidget(page)

    def _build_settings(self) -> None:
        page, layout = self._page(PAGES[6])
        validate = QPushButton("Validar ruleset incluido"); validate.clicked.connect(self.validate_rules)
        import_zip = QPushButton("Importar ruleset ZIP"); import_zip.clicked.connect(self.import_ruleset)
        backup = QPushButton("Exportar copia completa"); backup.clicked.connect(self.backup_database)
        restore = QPushButton("Restaurar copia verificada"); restore.clicked.connect(self.restore_database)
        layout.addWidget(validate); layout.addWidget(import_zip); layout.addWidget(backup); layout.addWidget(restore)
        self.settings_message = QLabel(); self.settings_message.setWordWrap(True); layout.addWidget(self.settings_message)
        layout.addStretch(); self.pages.addWidget(page)

    def _build_debug(self) -> None:
        page, layout = self._page(PAGES[7]); self.debug_text = QTextEdit(); self.debug_text.setReadOnly(True)
        layout.addWidget(self.debug_text); self.pages.addWidget(page)

    def _build_evaluations(self) -> None:
        page, layout = self._page(PAGES[8]); form = QFormLayout()
        self.test_combo = QComboBox(); self.test_combo.currentIndexChanged.connect(self._test_changed)
        self.test_result = QDoubleSpinBox(); self.test_result.setRange(-100000, 100000); self.test_result.setDecimals(2)
        self.test_unit = QLineEdit(); self.test_unit.setPlaceholderText("kg, s, repeticiones…")
        self.test_protocol = QTextEdit(); self.test_protocol.setReadOnly(True); self.test_protocol.setMaximumHeight(90)
        form.addRow("Prueba", self.test_combo); form.addRow("Resultado", self.test_result)
        form.addRow("Unidad", self.test_unit); form.addRow("Protocolo", self.test_protocol); layout.addLayout(form)
        save = QPushButton("Registrar evaluación inmutable"); save.clicked.connect(self.save_test_result); layout.addWidget(save)
        self.test_message = QLabel(); layout.addWidget(self.test_message)
        self.test_history = QTableWidget(0, 3); self.test_history.setHorizontalHeaderLabels(["Fecha", "Prueba", "Resultado"])
        self.test_history.horizontalHeader().setStretchLastSection(True); layout.addWidget(self.test_history); self.pages.addWidget(page)

    def _build_placeholder(self, name: str) -> None:
        page, layout = self._page(name)
        layout.addWidget(QLabel("Vista preparada para ampliar el catálogo sin introducir decisiones deportivas en la UI."))
        layout.addStretch(); self.pages.addWidget(page)

    def _require_user(self) -> bool:
        if self.current_user_id is None:
            QMessageBox.warning(self, "Falta usuario", "Crea o selecciona un usuario primero."); return False
        return True

    def refresh_users(self) -> None:
        if self.session_factory is None: return
        selected = self.current_user_id; self.user_combo.blockSignals(True); self.user_combo.clear()
        with self.session_factory() as session:
            for user in listar_usuarios(session): self.user_combo.addItem(user.alias, user.id)
        self.user_combo.blockSignals(False)
        if self.user_combo.count():
            index = self.user_combo.findData(selected) if selected else 0
            self.user_combo.setCurrentIndex(max(0, index)); self._user_changed(self.user_combo.currentIndex())

    def refresh_rulesets(self) -> None:
        if self.session_factory is None: return
        selected = self.ruleset_combo.currentData(); self.ruleset_combo.clear()
        with self.session_factory() as session:
            packages = session.scalars(select(RulePackageModel).order_by(RulePackageModel.package_id, RulePackageModel.version))
            for package in packages:
                self.ruleset_combo.addItem(f"{package.package_id} {package.version} [{package.status}]", package.id)
        if selected:
            index = self.ruleset_combo.findData(selected)
            if index >= 0: self.ruleset_combo.setCurrentIndex(index)

    def refresh_tests(self) -> None:
        if self.session_factory is None: return
        self.test_combo.clear()
        with self.session_factory() as session:
            for test in session.scalars(select(TestModel).order_by(TestModel.name)):
                self.test_combo.addItem(test.name, test.id)
        self._test_changed(self.test_combo.currentIndex())

    def _test_changed(self, index: int) -> None:
        if index < 0 or self.session_factory is None: return
        with self.session_factory() as session:
            test = session.get(TestModel, self.test_combo.itemData(index))
            self.test_protocol.setPlainText(test.protocol if test else "")

    def refresh_test_history(self) -> None:
        if self.current_user_id is None or self.session_factory is None: return
        with self.session_factory() as session:
            rows = list(session.scalars(select(TestHistoryModel).where(
                TestHistoryModel.user_id == self.current_user_id
            ).order_by(TestHistoryModel.performed_at.desc())))
        self.test_history.setRowCount(len(rows))
        for row, item in enumerate(rows):
            for col, value in enumerate((item.performed_at.isoformat(timespec="minutes"), item.test_id, f"{item.result:g} {item.unit}")):
                self.test_history.setItem(row, col, QTableWidgetItem(str(value)))

    def _user_changed(self, index: int) -> None:
        self.current_user_id = self.user_combo.itemData(index) if index >= 0 else None
        self.load_context_form(); self.refresh_plan(); self.refresh_test_history()

    def load_context_form(self) -> None:
        if self.current_user_id is None or self.session_factory is None: return
        with self.session_factory() as session:
            context = cargar_contexto_usuario(session, self.current_user_id)
        objective_index = self.objective.findText(context["objective"])
        if objective_index >= 0: self.objective.setCurrentIndex(objective_index)
        self.max_minutes.setValue(context["availability"]["max_minutes"])
        selected_days = set(context["availability"]["days"])
        for index, item in enumerate(self.day_checks): item.setChecked(index in selected_days)
        self.wall.setChecked(context["equipment"].get("wall", False))
        self.hangboard.setChecked(context["equipment"].get("hangboard", False))
        limitation_index = self.finger_limitation.findText(context["limitations"].get("fingers", "ninguna"))
        if limitation_index >= 0: self.finger_limitation.setCurrentIndex(limitation_index)

    def save_profile(self) -> None:
        if self.session_factory is None: return
        try:
            with self.session_factory.begin() as session:
                user = guardar_perfil(session, {"alias": self.alias.text().strip(), "age": self.age.value(),
                    "experience_years": self.experience.value(), "level": self.level.currentText(), "modality": self.modality.currentText()})
                user_id = user.id
            self.current_user_id = user_id; self.profile_message.setText("Perfil guardado."); self.refresh_users()
        except Exception as exc: self.profile_message.setText(f"No se guardó: {exc}")

    def save_context(self) -> None:
        if not self._require_user() or self.session_factory is None: return
        try:
            with self.session_factory.begin() as session:
                guardar_contexto_usuario(session, self.current_user_id, objective=self.objective.currentText(),
                    weekdays=[i for i, item in enumerate(self.day_checks) if item.isChecked()], max_minutes=self.max_minutes.value(),
                    equipment={"wall": self.wall.isChecked(), "hangboard": self.hangboard.isChecked()},
                    limitations={"fingers": self.finger_limitation.currentText()})
            self.context_message.setText("Contexto guardado.")
        except Exception as exc: self.context_message.setText(f"No se guardó: {exc}")

    def generate_current_plan(self) -> None:
        if not self._require_user() or self.session_factory is None: return
        try:
            with self.session_factory.begin() as session:
                context = cargar_contexto_usuario(session, self.current_user_id)
                package_id = self.ruleset_combo.currentData()
                package = cargar_rule_package_db(session, package_id) if package_id else None
                plan = generar_plan(session, user_id=self.current_user_id, package=package, context=context)
                self.current_plan_id = plan.id
            self.refresh_plan(); self.navigation.setCurrentRow(3)
        except Exception as exc: QMessageBox.critical(self, "No se generó el plan", str(exc))

    def refresh_plan(self) -> None:
        if self.session_factory is None or self.current_user_id is None: return
        with self.session_factory() as session:
            plan = ultimo_plan(session, self.current_user_id)
            if plan is None:
                self.current_plan_id = None; self.dashboard_status.setText("Perfil listo; guarda el contexto y genera un plan."); return
            self.current_plan_id = plan.id; sessions = listar_sesiones(session, plan.id)
            self.dashboard_status.setText(f"Plan #{plan.id} · ruleset {plan.package_version} · {len(sessions)} sesiones")
            self.plan_summary.setText(f"Plan #{plan.id} · snapshot conservado · ruleset {plan.package_version}")
            self.plan_table.setRowCount(len(sessions)); self.session_combo.clear()
            for row, item in enumerate(sessions):
                for col, value in enumerate((item.scheduled_date.isoformat(), item.objective, item.duration_minutes)):
                    self.plan_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.session_combo.addItem(f"{item.scheduled_date} · {item.objective}", item.id)
            self.debug_text.setPlainText(json.dumps(plan.rules_snapshot, ensure_ascii=False, indent=2, default=str))
        self.refresh_history()

    def save_feedback(self) -> None:
        session_id = self.session_combo.currentData()
        if not session_id or self.session_factory is None: return
        try:
            with self.session_factory.begin() as session:
                if session.scalar(select(SessionFeedbackModel).where(SessionFeedbackModel.session_id == session_id)):
                    raise ValueError("Esta sesión ya tiene registro; el historial no se sobrescribe")
                registrar_sesion(session, session_id, {"completion": self.completion.currentText(),
                    "completion_percent": self.completion_percent.value(), "rpe": self.rpe.value(),
                    "fatigue": self.fatigue.value(), "pain": self.pain.value(),
                    "details": {"comments": self.feedback_notes.toPlainText()}})
            self.feedback_message.setText("Entrenamiento registrado.")
        except Exception as exc: self.feedback_message.setText(f"No se guardó: {exc}")

    def save_test_result(self) -> None:
        if not self._require_user() or self.session_factory is None: return
        test_pk = self.test_combo.currentData(); unit = self.test_unit.text().strip()
        if not test_pk or not unit:
            self.test_message.setText("Selecciona una prueba e indica la unidad."); return
        try:
            with self.session_factory.begin() as session:
                test = session.get(TestModel, test_pk)
                package_id = self.ruleset_combo.currentData()
                package = session.get(RulePackageModel, package_id) if package_id else None
                ejecutar_reevaluacion(
                    session, self.current_user_id, test.test_id, self.test_result.value(), unit,
                    test.protocol, package.version if package else "UNVERSIONED",
                )
            self.test_message.setText("Evaluación registrada sin modificar resultados anteriores.")
            self.refresh_test_history()
        except Exception as exc: self.test_message.setText(f"No se guardó: {exc}")

    def export_plan(self) -> None:
        if not self.current_plan_id or self.session_factory is None: return
        target, _ = QFileDialog.getSaveFileName(self, "Exportar plan", f"plan-{self.current_plan_id}.pdf", "PDF (*.pdf)")
        if not target: return
        with self.session_factory() as session:
            plan = session.get(PlanModel, self.current_plan_id)
            sessions = listar_sesiones(session, self.current_plan_id)
            exportar_plan_pdf(plan, sessions, Path(target))
        self.plan_summary.setText(f"Plan exportado en {target}")

    def refresh_history(self) -> None:
        if not self.current_plan_id or self.session_factory is None: return
        with self.session_factory() as session:
            rows = list(session.scalars(select(DecisionLogModel).where(DecisionLogModel.plan_id == self.current_plan_id).order_by(DecisionLogModel.id)))
            self.history_table.setRowCount(len(rows))
            for row, item in enumerate(rows):
                values = (item.rule_id, item.action, item.input_values.get("objective"), item.previous_value, item.new_value)
                for col, value in enumerate(values): self.history_table.setItem(row, col, QTableWidgetItem(str(value)))

    def validate_rules(self) -> None:
        if self.package_path is None: return
        errors = validate_rule_package(self.package_path); self.settings_message.setText("Ruleset válido." if not errors else "\n".join(errors))

    def import_ruleset(self) -> None:
        source, _ = QFileDialog.getOpenFileName(self, "Importar ruleset", "", "Rule package (*.zip)")
        if not source or self.session_factory is None: return
        try:
            with self.session_factory.begin() as session: importar_ruleset_zip(session, Path(source))
            self.refresh_rulesets(); self.settings_message.setText("Ruleset importado atómicamente.")
        except Exception as exc:
            self.settings_message.setText(f"No se importó: {exc}")

    def backup_database(self) -> None:
        target, _ = QFileDialog.getSaveFileName(self, "Guardar copia", "climber-training-backup.db", "SQLite (*.db)")
        if target:
            export_backup(Settings.load().data_dir / "climber_training.db", Path(target)); self.settings_message.setText("Copia verificada creada.")

    def restore_database(self) -> None:
        source, _ = QFileDialog.getOpenFileName(self, "Seleccionar copia", "", "SQLite (*.db)")
        if not source: return
        answer = QMessageBox.question(self, "Confirmar restauración", "Se reemplazará la base actual y deberás reiniciar. ¿Continuar?")
        if answer == QMessageBox.StandardButton.Yes:
            bind = self.session_factory.kw.get("bind") if self.session_factory is not None else None
            if bind is not None: bind.dispose()
            restore_backup(Path(source), Settings.load().data_dir / "climber_training.db")
            self.settings_message.setText("Copia restaurada. Reinicia la aplicación.")
