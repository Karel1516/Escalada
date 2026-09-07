# Entrenamiento Escalada

Aplicación de escritorio local para crear perfiles, evaluar reglas declarativas y generar planes auditables. El motor no contiene protocolos deportivos codificados: carga paquetes JSON versionados y conserva el contexto, las reglas y los parámetros que produjeron cada decisión.

> Estado: **entrega técnica 0.1.0**. El ruleset `demo` sirve para comprobar el software. El paquete `1.0.0-candidate` está en `RESEARCH` y no debe tratarse como consejo médico ni prescripción validada.

## Ejecutar en desarrollo

Requiere Python 3.12 o 3.13 (PySide6 puede no ofrecer todavía ruedas para versiones más nuevas).

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
alembic upgrade head
entrenamiento-escalada
```

La base se crea en `%LOCALAPPDATA%\ClimberTraining\climber_training.db`, fuera de la instalación. Para una prueba aislada: `CLIMBER_TRAINING_DATA_DIR=C:\ruta\temporal`.

## Pruebas y validación

```powershell
python -m pytest
climber-rules validate rules\demo
climber-rules validate rules\1.0.0-candidate
```

## Empaquetado

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

El script genera un ejecutable PyInstaller y, si Inno Setup está instalado, un instalador. La base personal nunca se incrusta en el ejecutable.

Documentación: [arquitectura](docs/ARCHITECTURE.md), [motor](docs/RULE_ENGINE.md), [protocolo de investigación](docs/RESEARCH_PROTOCOL.md), [revisión de evidencia](docs/EVIDENCE_REVIEW.md), [usuario](docs/USER_GUIDE.md), [respaldo](docs/BACKUP_AND_RESTORE.md) y [limitaciones](docs/LIMITATIONS.md).
