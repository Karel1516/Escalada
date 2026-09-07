# Motor de reglas

## Forma

Una regla declara `condition`, `actions`, `rule_type`, `priority`, `rationale`, `classification` y `evidence_status`. Las condiciones son hojas o grupos `AND`/`OR`. El catálogo admite EQ, NEQ, GT, GTE, LT, LTE, BETWEEN, IN, NOT_IN, EXISTS y NOT_EXISTS.

## Resolución

Precedencia: `SAFETY (500) > EXCLUSION (400) > ELIGIBILITY (300) > PRESCRIPTION/otros (200) > PREFERENCE (100)`. Luego se comparan prioridad y RuleID, haciendo el resultado independiente del orden del JSON. Inclusión/exclusión del mismo ejercicio y permitir/bloquear progresión comparten una clave de conflicto. El ganador queda registrado.

## Seguridad

Solo se despachan acciones del enum `ActionType`; los valores son JSON. No se evalúan expresiones arbitrarias. Las referencias se validan antes de importar. El modo debug registra regla y resultado, y cada acción aplicada produce una `Decision` con entrada, valor anterior/nuevo, RuleID y versión.

## Versionado

- PATCH: corrección que no cambia resultados deportivos esperados.
- MINOR: nuevas reglas/parámetros compatibles o cambio esperado acotado.
- MAJOR: cambio incompatible de esquema/semántica o conducta ampliamente distinta.

Una versión usada nunca se edita: se clona bajo una versión nueva. Solo un paquete `ACTIVE` validado puede ser predeterminado; DEMO es `TESTING` y el candidato es `RESEARCH`.
