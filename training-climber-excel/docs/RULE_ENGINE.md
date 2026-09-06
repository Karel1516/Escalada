# Diseño del Rule Engine

Cada regla tiene metadatos; una o más condiciones agrupadas; cero o más acciones. Las condiciones de un grupo se unen con `AND`; los grupos se unen con `OR`. Operadores soportados: `EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `BETWEEN`, `IN`, `NOT_IN`, `EXISTS`, `NOT_EXISTS`.

Las acciones usan un catálogo cerrado: `INCLUDE/EXCLUDE_EXERCISE`, `INCLUDE/EXCLUDE_CATEGORY`, setters de prescripción, límites, multiplicadores, frecuencia/carga/RPE/RIR, progreso, descarga, reevaluación y advertencias. Un valor `PARAM:ID` se resuelve contra la versión del paquete.

## Algoritmo

1. Validar paquete e integridad de referencias.
2. Construir contexto a partir de perfil, objetivos, disponibilidad, equipo, limitaciones y feedback.
3. Evaluar reglas activas sin efectos laterales.
4. Convertir coincidencias en propuestas de acción.
5. Ordenar por precedencia, prioridad y RuleID.
6. Detectar propuestas incompatibles y escoger ganador determinista.
7. Aplicar al borrador del plan y registrar cada decisión.
8. Confirmar el plan como nuevas filas; nunca actualizar ciclos pasados.

## Validación

Rechaza RuleID duplicado, operador/acción desconocido, SemVer inválido, prioridad no numérica, rango invertido y referencias inexistentes a parámetros, ejercicios o fuentes. Una regla de producción sin evidencia o justificación explícita queda marcada; un paquete con errores no puede activarse.
