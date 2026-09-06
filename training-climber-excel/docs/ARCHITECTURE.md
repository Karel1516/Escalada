# Arquitectura

## Vista general

```text
Hojas de entrada -> Contexto normalizado -> Motor de reglas -> Resolver -> Plan
                                             |                |        |
Ruleset + condiciones + acciones + parámetros+                +-> conflictos
Ejercicios + equipo + limitaciones ----------------------------+-> decisiones
Feedback anterior ---------------------------------------------+-> adaptación
```

La interfaz vive en las hojas 00–09. Las tablas maestras viven en 10–19. Historial, configuración y depuración viven en 20–23. Ninguna decisión deportiva importante depende de una dirección fija de celda: el código resuelve tablas y columnas por nombre.

## Componentes

- **Persistencia:** ListObjects de Excel; altas append-only para planes, resultados, feedback y decisiones.
- **Motor:** interpreta operadores y acciones de catálogo; no evalúa texto como VBA.
- **Resolver:** orden total por precedencia de tipo, prioridad descendente y RuleID ascendente.
- **Planificador:** selecciona ejercicios elegibles, aplica acciones ganadoras, distribuye sesiones y recorta por presupuesto temporal.
- **Trazabilidad:** cada mutación relevante escribe entrada/salida serializadas, regla y versión.
- **Paquetes:** carpetas portables con `package.json` y CSV; el libro conserva la versión usada.

## Modelo de datos

| Entidad | Clave | Relaciones principales |
|---|---|---|
| RulePackages | Version | Rules, Parameters |
| Rules | Version + RuleID | Conditions, Actions, RuleEvidence |
| Parameters | Version + ParameterID | Actions y RuleParameters |
| Evidence | SourceID | RuleEvidence, Exercises, Tests |
| Exercises | ExerciseID | SessionExercises, Actions |
| Tests | TestID | TestHistory |
| Users | UserID | equipo, limitaciones, objetivos, planes |
| Plans | PlanID | Sessions, DecisionLog; fija Version |
| Sessions | SessionID | SessionExercises, Feedback |

Las relaciones N:M se materializan mediante tablas puente. Los datos históricos incluyen claves y versión, evitando depender del estado actual de maestros.

## Precedencia formal

`SAFETY > EXCLUSION > ELIGIBILITY > PRESCRIPTION > PREFERENCE`. Dentro de la misma clase gana mayor `Priority`; un empate se resuelve por `RuleID` lexicográfico. Las acciones exclusivas dominan inclusiones del mismo objetivo. Todos los candidatos y el ganador quedan registrados.

## Riesgos y límites

Excel no es un servidor transaccional: se asume un usuario a la vez. La integridad se valida antes de activar paquetes. No se proporciona diagnóstico médico. El corpus de evidencia no prueba cada combinación de dosis, población y nivel; donde falta soporte directo se conserva `UNCERTAIN` o `EXPERT_HEURISTIC`.
