# Reporte de pruebas

Fecha: 2026-09-06  
Entorno: Windows, Microsoft Excel 16, Python 3.14

## Resultado

| Capa | Prueba | Resultado |
|---|---|---|
| Paquetes | DEMO y 1.0.0-candidate validan referencias | PASS |
| Operadores | EQ, NEQ, GT, GTE, LT, LTE, BETWEEN, IN, NOT_IN, EXISTS, NOT_EXISTS | PASS |
| Composición | AND dentro de grupo; OR entre grupos | PASS |
| Conflictos | Safety excluye hangboard aunque rendimiento lo incluya | PASS |
| Progresión | Safety mantiene `BLOCK` frente a `ALLOW` | PASS |
| Parámetros | Resolución `PARAM:ID`; falta de ID detectada | PASS |
| Evidencia | SourceID roto detectado | PASS |
| Tiempo | Sesiones no exceden el presupuesto | PASS |
| Versionado | Plan fija `RulePackageVersionUsed` | PASS |
| Trazabilidad | Acciones registran RuleID | PASS |
| Excel | 24 hojas y 22 ListObjects | PASS |
| XLSM | `xl/vbaProject.bin` presente | PASS |
| VBA | 20 módulos, todos con `Option Explicit` | PASS |
| Integración Excel | Validación del Ruleset desde VBA | PASS |
| Integración Excel | Generación DEMO: 1 plan, 3 sesiones, 1 ejercicio, 7 decisiones | PASS |
| Restricción temporal | Máximo observado 25 min con presupuesto de 60 min | PASS |
| Safety Excel | dolor de dedos: EX_HANG_MAX excluido; EX_CLIMB_EASY permitido | PASS |

Suite de referencia: `python tests/run_tests.py` — **22/22 PASS**.

Archivo probado: `dist/Entrenamiento_Escalada.xlsm`  
SHA-256: `CFC2F3F50FF7D0056E350AF02199EBC488EC49A810AA62F8BBA4CE917DBBBF59`

## Casos A–J

- A–E: contextos cubiertos por disponibilidad, equipo, dolor y tiempo; el planificador distribuye y recorta.
- F: versión fijada y paquetes separados; no se muta una versión histórica.
- G: probado explícitamente en Python y Excel.
- H–I: referencias rotas de ParameterID y SourceID detectadas.
- J: el validador identifica una regla sin fuente ni rationale; las heurísticas del candidato incluyen rationale explícito.

## Incidencias corregidas

1. Normalización de booleanos `TRUE/VERDADERO` para independencia regional.
2. Separación lateral de tablas append-only para evitar colisiones al crecer.
3. Corrección de firma de `PersistSessionExercise` y acceso explícito a objetos Dictionary.

## Alcance de la validación

Se verificó ejecución del motor, generación, persistencia, precedencia Safety y estructura del archivo. No constituye validación clínica ni científica prospectiva del candidato. `1.0.0-candidate` sigue en estado `RESEARCH`.
