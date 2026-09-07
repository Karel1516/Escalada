from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas


def exportar_plan_pdf(plan, sessions, destination: Path) -> Path:
    canvas = Canvas(str(destination), pagesize=A4)
    y = 800
    canvas.setTitle(f"Plan {plan.id}")
    canvas.drawString(40, y, f"Plan #{plan.id} · Ruleset {plan.package_version}")
    for session in sessions:
        y -= 24
        canvas.drawString(40, y, f"{session.scheduled_date}: {session.objective} ({session.duration_minutes} min)")
        if y < 60:
            canvas.showPage(); y = 800
    canvas.save()
    return destination
