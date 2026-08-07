; Inno Setup Script - AcademiaFutbol
; Requiere: Inno Setup 6.7+

#define MyAppName "AcademiaFutbol"
#define MyAppVersion "1.0.0"
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
OutputDir=installer\Output
OutputBaseFilename=AcademiaFutbol-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x86compatible
ArchitecturesInstallIn64BitMode=x86compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
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

[Dirs]
Name: "{app}\database"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName} ahora"; Flags: nowait postinstall skipifsilent

[Code]
function GetInstallPath(Param: String): String;
begin
  Result := ExpandConstant('{app}');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Crear carpeta de backups si OneDrive no esta disponible
    if not DirExists(ExpandConstant('{localappdata}\BackupsAcademia')) then
      CreateDir(ExpandConstant('{localappdata}\BackupsAcademia'));
  end;
end;
