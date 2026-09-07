# Respaldo y restauración

La base predeterminada está en `%LOCALAPPDATA%\ClimberTraining`. Cierra la aplicación antes de una restauración manual.

`export_backup()` usa la API de backup de SQLite y verifica integridad. `restore_backup()` abre la copia como solo lectura, comprueba `PRAGMA integrity_check`, valida tablas de la aplicación, copia a un archivo temporal en el destino y finalmente usa reemplazo atómico.

Antes de migrar en producción debe llamarse a `export_backup()` con nombre fechado. Una actualización reemplaza binarios, nunca la carpeta de datos. Conserve copias fuera del equipo. Esta entrega aún no expone estos métodos en un diálogo gráfico.
