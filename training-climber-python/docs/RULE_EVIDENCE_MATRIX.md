# Matriz Rule → Evidence

| RuleID | Acción | Fuente | Relación | Confianza | Nota |
|---|---|---|---|---|---|
| DEMO-SELECT-001 | incluye DEMO_HANG | DESIGN-001 | RATIONALE | N/A | Prueba técnica |
| DEMO-SAFETY-001 | excluye DEMO_HANG | DESIGN-001 | RATIONALE | N/A | Precaución sintética |
| DEMO-BASE-001 | incluye práctica DEMO | DESIGN-001 | RATIONALE | N/A | Prueba técnica |
| CANDIDATE-SAFETY-FINGER-001 | bloqueo y aviso | R2, R8 | SAFETY | baja | No establece tratamiento ni umbral seguro |
| CANDIDATE-FINGER-ELIGIBILITY-001 | habilita fuerza de dedos | R1, R8, R9 | SUPPORT/BACKGROUND | baja–moderada | Umbral de 2 años: heurística explícita |
| CANDIDATE-CLIMBING-001 | práctica específica | R1 | BACKGROUND | limitada | Sin dosis |
| CANDIDATE-FINGER-ENDURANCE-001 | habilita resistencia de dedos en avanzados | R9, R11 | DIRECT/BACKGROUND | limitada | No extrapolar a principiantes; sin dosis universal |
| CANDIDATE-CAMPUS-ELIGIBILITY-001 | habilita campus en avanzados/élite | R12 | DIRECT_SUPPORT | limitada | No demuestra seguridad ni frecuencia óptima |

La fuente canónica legible por máquina está en cada `rule_evidence.json`. Ninguna correlación de rendimiento se ha convertido directamente en dosis.
