# Matriz de requerimientos

La fuente normativa completa es `../docs/prompt_maestro.md` en el repositorio padre. Esta matriz agrupa los 50 RF y los entregables verificables.

| Área | IDs | Implementación | Verificación |
|---|---:|---|---|
| Usuario, nivel, modalidad, objetivos | RF-001–004 | Formularios tabulares y `GuardarPerfil` | Casos A–C |
| Disponibilidad, equipo, limitaciones, safety | RF-005–008 | Contexto normalizado; filtros y precedencia Safety | Casos D, E, G |
| Tests e historial | RF-009–011 | `tblTests`, selección declarativa, historial append-only | prueba de elegibilidad |
| Ejercicios y categorías | RF-012–013 | `tblExercises` con requisitos y evidencia | integridad referencial |
| Motor declarativo | RF-014–022 | condiciones, acciones, prioridad, precedencia y conflictos | suite de operadores |
| Parámetros | RF-023–024 | `tblParameters` y referencias `PARAM:` | caso H |
| Paquetes/versiones | RF-025–030 | SemVer, estados, validación y versión fijada al plan | caso F |
| Planificación | RF-031–034 | `GenerarPlan`, `GenerarSemana`, límite temporal y separación | casos A–E |
| Feedback/adaptación | RF-035–039 | registro append-only y acciones de progreso | pruebas de progresión |
| Auditoría/debug | RF-040–042 | `tblDecisionLog` y hoja Debug | trazabilidad determinista |
| Importación/validación | RF-043–046 | import/export CSV y validación referencial | H–J |
| Dashboard/PDF/UI | RF-047–050 | inicio, indicadores y exportación | inspección del libro |
| No funcionales | RNF-001–015 | módulos separados, ListObjects, sin Select/Activate, errores | revisión estática |
| Evidencia | INV-001–024 | evidencia verificada, relaciones N:M y etiquetas de incertidumbre | matriz y referencias |

## Criterios de salida

El libro debe abrir sin reparación, contener las 24 hojas, tablas nombradas, un Ruleset DEMO validable, historial no destructivo y código fuente reproducible. El candidato científico no se marca ACTIVE mientras continúe en revisión.
