# Matriz de requerimientos

Esta matriz condensa RF-001–051 del prompt maestro. “Base” significa implementado en la entrega 0.1; “siguiente” requiere ampliar la interfaz o validación experta.

| Bloque | RF | Resultado verificable | Estado 0.1 |
|---|---:|---|---|
| Perfil | 001–004 | Usuario, niveles/grados configurables, modalidad y objetivos | Flujo UI funcional; grados detallados pendientes |
| Contexto | 005–008 | Disponibilidad, equipo, limitaciones; Safety prevalece | Flujo UI + persistencia + prueba de precedencia |
| Evaluación | 009–011 | Catálogo y registro histórico inmutable | Modelo; catálogo ampliable siguiente |
| Ejercicios | 012–013 | Catálogo estructurado y categorías | JSON + modelo base |
| Motor | 014–022 | Reglas declarativas, operadores, acciones, prioridad y conflictos | Implementado y probado |
| Parámetros | 023–024 | Valores reutilizables fuera del código | Implementado y probado |
| Versionado | 025–030 | SemVer, estados, inmutabilidad, snapshot | Implementado en formato y modelos |
| Plan | 031–034 | Ciclo/semana, límite temporal y recuperación | Generación mínima; optimizador de carga siguiente |
| Feedback | 035–039 | Registro, progresión declarativa, nuevo ciclo, reevaluación | Registro UI inmutable + ramas DEMO de adaptación |
| Auditoría | 040–042 | DecisionID, explicación y debug | Implementado en motor/modelo |
| Paquetes | 043–046 | ZIP canónico, validación previa y activación segura | Importación DB atómica, exportación y validación |
| Experiencia | 047–050 | Dashboard, PDF y navegación | Recorrido principal funcional; reportes avanzados pendientes |
| Datos | 051 | Persistencia, backup/restauración atómicos y exportación | Alembic + respaldo previo + UI de copia/restauración |

## Criterios de aceptación cubiertos

CA-001–006, 009–025 y 027–032 cuentan con estructura o prueba automática. Evaluaciones completas, dashboards avanzados y validación en máquina limpia siguen pendientes. Véase `LIMITATIONS.md`.
