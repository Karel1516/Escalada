param([string]$PythonExe = "")
$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $project
if (-not $PythonExe) {
    $PythonExe = Join-Path $project ".venv\Scripts\python.exe"
}
if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "No existe el intérprete $PythonExe. Crea .venv o usa -PythonExe."
}
& $PythonExe -m pip install -e ".[dev]"
& $PythonExe -m pytest
& $PythonExe -m PyInstaller --noconfirm packaging/Entrenamiento_Escalada.spec
Write-Host "Ejecutable: $project\dist\Entrenamiento_Escalada.exe"
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($iscc) {
    & $iscc.Source packaging/installer.iss
} else {
    Write-Warning "Inno Setup no está instalado; se generó el ejecutable, no el instalador."
}
