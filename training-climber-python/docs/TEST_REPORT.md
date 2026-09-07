# Reporte de pruebas

Fecha: 2026-09-06. Entorno: Windows 11, Python 3.14.3, PySide6 6.11.2.

Resultado de fase 12: **36 pruebas aprobadas, 0 fallos** y **85% de cobertura total**. Los seis archivos canónicos de ambos paquetes pasaron JSON Schema, referencias y checksums. Las migraciones alcanzan `0002 (head)` y son idempotentes.

Cobertura ejecutada: operadores, AND/OR, Safety sobre rendimiento, parámetros, trazabilidad, referencias rotas, importación ZIP transaccional, exportación reproducible, copia/restauración, migración programática, casos A–J, adaptación por feedback, PDF, historial de evaluaciones, recorrido gráfico principal y smoke test de UI.

Empaquetado de fase 3: PyInstaller 6.22.2 produjo `dist/Entrenamiento_Escalada.exe` (66,482,288 bytes). El ejecutable arrancó con Qt offscreen, ejecutó Alembic hasta `0002`, sembró un ruleset y un test DEMO sin log de error; después fueron terminados sus dos procesos (bootloader y aplicación) por el test.

Las advertencias sobre `pysqlite2`, MySQL y PostgreSQL corresponden a backends opcionales no usados. Pendiente: casos e2e A–J completos, instalador Inno Setup en máquina limpia y restauración con fallo inyectado.
