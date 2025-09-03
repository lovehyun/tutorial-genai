; Minimal Inno Setup for Claude Desktop MCP agent (with inputs)

#define MyAppName    "NAS-NoDB-Scanner"
#define MyAppVersion "1.0.0"
#define MyPublisher  "GenAI Labs"
#define MyExeName    "NAS-Scanner.exe"
#define MyCompanyDir "GenAILabs"

[Setup]
AppId={{3D2A7B8B-1234-4A6A-9F90-ABCD12345678}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyPublisher}
DefaultDirName={pf}\{#MyCompanyDir}\{#MyAppName}
OutputBaseFilename=NAS-NoDB-Scanner-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
WizardStyle=modern
DisableProgramGroupPage=yes

[Files]
Source: "..\dist\{#MyExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "postinstall.ps1";              DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall.ps1";                DestDir: "{app}"; Flags: ignoreversion

[Run]
; 사용자가 입력한 값을 PowerShell에 전달
Filename: "powershell.exe"; \
  Parameters: "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File ""{app}\postinstall.ps1"" -ScanRoot ""{code:GetScanRoot}"" -AppDir ""{app}"" -DataDir ""{code:GetDataDir}"" -IndexDb ""{code:GetIndexDb}"" -ClaudeRequired"; \
  StatusMsg: "Claude용 MCP 설정을 구성 중입니다..."; \
  Flags: runhidden waituntilterminated

[UninstallRun]
; 완전 제거(ProgramData + Claude 등록까지 삭제). 원하는 옵션만 남기면 됩니다.
Filename: "powershell.exe"; \
  Parameters: "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File ""{app}\uninstall.ps1"" -AppDir ""{app}"" -DataDir ""{code:GetDataDirAtUninstall}"" -RemoveData -RemoveClaude"; \
  Flags: runhidden waituntilterminated

[UninstallDelete]
; 위 UninstallRun에서 ProgramData를 지우므로 이 섹션은 생략 가능.
; 남겨두려면 아래 주석 해제하고 -RemoveData 옵션은 빼세요.
; Type: filesandordirs; Name: "{code:GetDataDirAtUninstall}"

[Code]
var
  Pg: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  { wpSelectDir 뒤에 설정 입력 페이지 생성 }
  Pg := CreateInputQueryPage(
    wpSelectDir,
    'NAS 스캔 설정',
    '필수 설정을 입력하세요.',
    '※ SCAN_ROOT는 UNC 경로를 권장합니다 (예: \\192.168.0.10\docs).'
  );
  { 0: ScanRoot (위) }
  Pg.Add('Scan root (UNC):', False);
  { 1: DataDir (아래) }
  Pg.Add('Data directory:', False);
  { 2: IndexDb (아래) }
  Pg.Add('Index DB path:', False);

  { 기본값 }
  Pg.Values[0] := '\\192.168.0.10\docs';
  Pg.Values[1] := 'C:\ProgramData\GenAILabs\NAS-NoDB-Scanner';
  Pg.Values[2] := 'C:\ProgramData\GenAILabs\NAS-NoDB-Scanner\nas_index.db';
end;

function IsUNC(const S: string): Boolean;
begin
  { 매우 단순한 UNC 체크 }
  Result := (Copy(S,1,2)='\\') and (Pos('\', Copy(S,3,MaxInt))>0);
end;

function DirExistsOrParentOK(const S: string): Boolean;
begin
  Result := DirExists(S);
  if not Result then
    Result := (Length(S)>=3) and (S[2]=':') and (S[3]='\'); { C:\... 형태면 생성 가능하다고 판단 }
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  scanRoot, dataDir, indexDb: string;
begin
  Result := True;
  if CurPageID = Pg.ID then
  begin
    scanRoot := Trim(Pg.Values[0]);
    dataDir  := Trim(Pg.Values[1]);
    indexDb  := Trim(Pg.Values[2]);

    if scanRoot = '' then
    begin
      MsgBox('Scan root는 필수입니다.', mbError, MB_OK);
      Result := False; exit;
    end;

    if not IsUNC(scanRoot) then
    begin
      MsgBox('Scan root는 UNC 경로(예: \\서버\공유)로 입력하세요. 드라이브 문자는 세션에 따라 보이지 않을 수 있습니다.', mbError, MB_OK);
      Result := False; exit;
    end;

    if dataDir = '' then
    begin
      MsgBox('Data directory는 필수입니다.', mbError, MB_OK);
      Result := False; exit;
    end;

    if not DirExistsOrParentOK(dataDir) then
    begin
      MsgBox('Data directory 경로가 유효하지 않습니다: ' + dataDir, mbError, MB_OK);
      Result := False; exit;
    end;

    if indexDb = '' then
      Pg.Values[2] := AddBackslash(dataDir) + 'nas_index.db'
    else
      if Pos('\', indexDb) = 0 then
      begin
        MsgBox('Index DB는 전체 경로를 입력하세요 (예: C:\ProgramData\...\nas_index.db).', mbError, MB_OK);
        Result := False; exit;
      end;
  end;
end;

function GetScanRoot(Param: string): string;
begin
  Result := Pg.Values[0];
end;

function GetDataDir(Param: string): string;
begin
  Result := Pg.Values[1];
end;

function GetIndexDb(Param: string): string;
begin
  if Trim(Pg.Values[2]) = '' then
    Result := AddBackslash(Pg.Values[1]) + 'nas_index.db'
  else
    Result := Pg.Values[2];
end;

function GetDataDirAtUninstall(Param: string): string;
begin
  { 설치 시 입력값을 레지스트리에 저장/복원하려면 확장 가능.
    간단히 기본값을 반환하도록 둡니다. }
  Result := 'C:\ProgramData\GenAILabs\NAS-NoDB-Scanner';
end;
