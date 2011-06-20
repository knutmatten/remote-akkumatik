; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Remote Akkumatik Display"
#define MyAppVersion "0.5"
#define MyAppURL "http://www.calmar.ws/akkumatik/"
#define MyAppExeName "remote_akkumatik.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{57C7D8F6-0E9A-4E64-BC30-EEEB09A30ADC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName=Remote Akkumatik Display
AllowNoIcons=yes
LicenseFile=C:\Dokumente und Einstellungen\calmar\Desktop\calmarc-remote-akkumatik\COPYING
OutputDir=C:\Dokumente und Einstellungen\calmar\Desktop
OutputBaseFilename=remote-akkumatik-display-install
SetupIconFile=C:\Dokumente und Einstellungen\calmar\Desktop\calmarc-remote-akkumatik\ra.ico
Compression=lzma
SolidCompression=yes
ChangesEnvironment=yes
;UninstallDisplayIcon={app}\MyProg.exe,1


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "C:\Dokumente und Einstellungen\calmar\Desktop\calmarc-remote-akkumatik\dist\remote_akkumatik.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Dokumente und Einstellungen\calmar\Desktop\calmarc-remote-akkumatik\dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,...}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon
; IconFilename: "{app}\myicon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, "&", "&&")}}"; Flags: nowait postinstall skipifsilent

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\gnuplot\bin"; Check: NeedsAddPath('{app}\gnuplot\bin')

#[UninstallDelete]
#Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\gnuplot\bin"; Check: NeedsAddPath('{app}\gnuplot\bin')


[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_LOCAL_MACHINE, 
       'SYSTEM\CurrentControlSet\Control\Session Manager\Environment','Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  // look for the path with leading and trailing semicolon
  // Pos() returns 0 if not found
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;
