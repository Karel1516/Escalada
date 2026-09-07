# Arquitectura

## Capas

`domain` contiene entidades y catálogos estables sin importar framework. `rule_engine` interpreta datos seguros, resuelve conflictos y produce decisiones. `application` coordina transacciones y casos de uso. `infrastructure` implementa SQLAlchemy/SQLite, archivos, PDF y respaldo. `ui` traduce eventos PySide6; nunca consulta tablas directamente.

Flujo: contexto del usuario → paquete validado → evaluación determinista → resolución → plan/snapshot → sesiones → feedback → contexto del ciclo siguiente.

## Decisiones

- SQLite vive en la carpeta de datos del usuario; la instalación solo contiene semillas de lectura.
- No se usa `eval`, `exec` ni código introducido por el usuario.
- Planes, resultados y decisiones son append-only desde los casos de uso normales.
- Una transacción abarca la creación del plan, sesiones y log de decisiones.
- El motor puede probarse sin interfaz; la UI no contiene reglas deportivas.
- SQLAlchemy 2.x es la persistencia; Alembic mantiene el esquema.

## Seguridad y fallos

Claves foráneas SQLite se activan por conexión. Los errores de inicio llegan a un diálogo legible. La importación debe validar todo antes de abrir la transacción. No hay telemetría ni llamadas ocultas de red.
