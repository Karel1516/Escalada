# Limitaciones reales

- Es una entrega técnica inicial, no el producto completo descrito por los 51 RF.
- El recorrido perfil → contexto → evaluación → plan → feedback → trazabilidad funciona; escalas, tests deportivos validados y dashboards avanzados siguen incompletos.
- `generar_semana` es deliberadamente simple; no optimiza fatiga ni incompatibilidades complejas.
- La importación ZIP es atómica; falta un editor técnico gráfico completo y reconstrucción/exportación desde registros normalizados.
- Se generó y arrancó el `.exe` en desarrollo; falta probarlo en una máquina Windows limpia y generar el instalador Inno Setup.
- No se realizó revisión sistemática propia. La evidencia inicial no justifica dosis universales.
- El candidato 1.0.0 sigue en `RESEARCH`; no es producción.
- Los casos A–J tienen cobertura técnica; falta una validación e2e clínica/deportiva con datos reales y restauración bajo fallos simulados del sistema operativo.
- La entrega fue validada con Python 3.14.3; el proyecto declara compatibilidad desde Python 3.12, pero falta ejecutar la matriz completa 3.12/3.13.
