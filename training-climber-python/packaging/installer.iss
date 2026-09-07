#define MyAppName "Entrenamiento Escalada"
#define MyAppVersion "0.1.0"
[Setup]
AppId={{C9F0CA44-395A-4D2E-A6B0-4044A44B0619}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\Entrenamiento Escalada
DefaultGroupName={#MyAppName}
OutputDir=..\dist
OutputBaseFilename=Entrenamiento_Escalada_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
[Files]
Source: "..\dist\Entrenamiento_Escalada.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\Entrenamiento_Escalada.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\Entrenamiento_Escalada.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"
[Run]
Filename: "{app}\Entrenamiento_Escalada.exe"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent
