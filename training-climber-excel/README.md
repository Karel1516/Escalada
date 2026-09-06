# Entrenamiento de escalada — sistema versionado

Aplicación de prescripción dentro de Excel. El libro usa tablas como fuente de conocimiento, un motor VBA genérico para evaluar reglas declarativas y un registro append-only para conservar planes, sesiones y decisiones.

## Entregable

- `dist/Entrenamiento_Escalada.xlsm`: libro generado con hojas, tablas, interfaz y macros (cuando Excel permite acceso programático al proyecto VBA).
- `src/vba/`: código fuente importable y auditable.
- `src/python/rule_engine.py`: implementación de referencia usada para pruebas automatizadas.
- `rules/`: paquetes DEMO y 1.0.0-candidate, separados por estado y versión.
- `docs/`: arquitectura, requisitos, evidencia, matriz regla–evidencia y reporte de pruebas.

## Construcción

En PowerShell, desde la raíz del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\src\build_workbook.ps1
python .\tests\run_tests.py
```

Si Excel bloquea el acceso al proyecto VBA, habilite **Archivo > Opciones > Centro de confianza > Configuración del Centro de confianza > Configuración de macros > Confiar en el acceso al modelo de objetos de proyectos de VBA**, cierre Excel y vuelva a ejecutar el constructor. El script nunca afirma haber incrustado VBA si la verificación falla.

## Uso

1. Abra `dist/Entrenamiento_Escalada.xlsm` y habilite macros.
2. Complete las celdas amarillas de `01_PERFIL`, `02_OBJETIVOS`, `03_DISPONIBILIDAD`, `04_EQUIPO` y `05_EVALUACION`.
3. Use los botones de `00_INICIO`: guardar perfil, validar ruleset, generar plan, registrar sesión o exportar PDF.
4. Consulte `21_LOG_DECISIONES` para saber qué regla, parámetro y versión produjo cada decisión.

## Seguridad y alcance

No diagnostica ni sustituye valoración médica. Dolor o limitación activa dispara exclusiones y advertencias conservadoras. El paquete `DEMO` prueba el motor y no constituye prescripción validada. El paquete `1.0.0-candidate` permanece `RESEARCH`; sus reglas están etiquetadas por origen y no se activa automáticamente.

## Versionado

Se usa SemVer: PATCH corrige metadatos sin cambiar la intención de prescripción; MINOR añade reglas compatibles o modifica parámetros; MAJOR cambia semántica, precedencia o conducta incompatible. Un paquete usado por un plan se trata como inmutable.
