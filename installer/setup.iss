; Inno Setup Script - AcademiaFutbol
; Requiere: Inno Setup 6.7+

#define MyAppName "AcademiaFutbol"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Academia Deportiva"
#define MyAppURL "https://github.com/MoisesVillar19/AcademiaFutbol"
#define MyAppExeName "AcademiaFutbol.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableDirPage=no
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=AcademiaFutbol-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x86compatible
ArchitecturesInstallIn64BitMode=x86compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no
AppMutex=AcademiaFutbolMutex
VersionInfoVersion={#MyAppVersion}.0
VersionInfoDescription=Sistema de Gestion - Academia Deportiva
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\AcademiaFutbol\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\AcademiaFutbol\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\setup_onedrive.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_BLOQUEO.txt"; DestDir: "{app}"; Flags: ignoreversion

[INI]
; config.ini se genera en setup_onedrive.bat / CurStepChanged, no se empaqueta fijo
; Si el usuario ya tiene config.ini (actualización), no se sobreescribe

[Dirs]
Name: "{app}\database"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent

[Code]
function GetOneDrivePath(Param: String): String;
var
  Path: String;
begin
  Path := GetEnv('OneDrive');
  if Path = '' then Path := GetEnv('OneDriveConsumer');
  if Path = '' then Path := GetEnv('OneDriveCommercial');
  if (Path = '') or (not DirExists(Path)) then
    Path := ExpandConstant('{userdocs}\OneDrive');
  if DirExists(Path) then
    Result := Path
  else
    Result := '';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigPath, OneDrivePath, DBPath: String;
  Lines: TArrayOfString;
begin
  if CurStep = ssPostInstall then
  begin
    // No sobreescribir config.ini si ya existe (actualización)
    ConfigPath := ExpandConstant('{app}\config.ini');
    if FileExists(ConfigPath) then exit;

    OneDrivePath := GetOneDrivePath('');
    if OneDrivePath <> '' then
    begin
      // Crear estructura OneDrive central
      if not DirExists(OneDrivePath + '\Academia') then CreateDir(OneDrivePath + '\Academia');
      if not DirExists(OneDrivePath + '\Academia\fotos') then CreateDir(OneDrivePath + '\Academia\fotos');
      if not DirExists(OneDrivePath + '\Academia\comprobantes') then CreateDir(OneDrivePath + '\Academia\comprobantes');
      if not DirExists(OneDrivePath + '\BackupsAcademia') then CreateDir(OneDrivePath + '\BackupsAcademia');
      DBPath := OneDrivePath + '\Academia\academia.db';
      SetArrayLength(Lines, 7);
      Lines[0] := '[database]';
      Lines[1] := 'path=' + DBPath;
      Lines[2] := '';
      Lines[3] := '[backup]';
      Lines[4] := 'dir=' + OneDrivePath + '\BackupsAcademia';
      Lines[5] := '';
      Lines[6] := '[rutas]';
      SaveStringsToFile(ConfigPath, Lines, False);
      // fotos/comprobantes se resuelven via OneDrive\Academia\fotos si no están en config
    end
    else
    begin
      // Fallback local (sin OneDrive) — no crear, la app usará database\academia.db
      if not DirExists(ExpandConstant('{localappdata}\BackupsAcademia')) then
        CreateDir(ExpandConstant('{localappdata}\BackupsAcademia'));
    end;
  end;
end;
