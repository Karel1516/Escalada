# Modelo de datos

Entidades de identidad/contexto: `users`, `user_equipment`, `user_limitations`, `objectives`, `grade_scales`.

Conocimiento versionado: `rule_packages`, `rules`, `rule_conditions`, `rule_actions`, `parameters`, `rule_parameters`, `evidence`, `rule_evidence`, `exercises`, `tests`.

Historial: `plans`, `sessions`, `session_exercises`, `session_feedback`, `test_history`, `decision_log`.

Cada plan guarda `input_snapshot`, `rules_snapshot` y `package_version`. Las relaciones normalizadas permiten consulta; el snapshot permite explicar el resultado aunque exista una versión posterior. Borrar un usuario/paquete referenciado está restringido. Los resultados históricos no tienen operación de actualización en los servicios públicos.

La migración `0001` crea el mismo `MetaData` que usa la aplicación, evitando divergencia entre instalación limpia y desarrollo.
