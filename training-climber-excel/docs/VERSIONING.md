# Estrategia de versionado

- **DEMO / TESTING:** datos artificiales para verificar semántica del motor.
- **1.0.0-candidate / RESEARCH:** propuesta informada por evidencia; no activa por defecto.
- **ACTIVE:** solo tras validación técnica, revisión de vínculos científicos y aprobación humana responsable.

SemVer se interpreta sobre el conocimiento: MAJOR para incompatibilidad de semántica o seguridad; MINOR para nuevas reglas o cambios de dosis; PATCH para correcciones no prescriptivas. Publicar crea un paquete nuevo. Los planes almacenan `RulePackageVersionUsed` y no leen retrospectivamente otra versión.
