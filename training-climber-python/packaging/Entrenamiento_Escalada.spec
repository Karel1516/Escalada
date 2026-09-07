from pathlib import Path

root = Path(SPECPATH).parent
a = Analysis(
    [str(root / "src" / "climber_training" / "main.py")],
    pathex=[str(root / "src")],
    datas=[(str(root / "rules"), "rules"), (str(root / "alembic"), "alembic")],
    hiddenimports=["sqlalchemy.dialects.sqlite", "logging.config"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="Entrenamiento_Escalada", console=False, icon=None,
)
