param(
  [Parameter(Mandatory=$true)][string]$ScanRoot,
  [Parameter(Mandatory=$true)][string]$AppDir,
  [Parameter(Mandatory=$true)][string]$DataDir,
  [string]$IndexDb,
  [switch]$ClaudeRequired
)

$ErrorActionPreference = "Stop"

if (-not $ScanRoot.StartsWith('\\')) {
  throw "ScanRoot는 UNC 경로여야 합니다. 예: \\192.168.0.10\docs"
}
if ([string]::IsNullOrWhiteSpace($IndexDb)) {
  $IndexDb = Join-Path $DataDir "nas_index.db"
}

# ProgramData 준비 + .env
New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
$EnvPath = Join-Path $DataDir ".env"
@"
SCAN_ROOT=$ScanRoot
INDEX_DB=$IndexDb
"@ | Out-File -FilePath $EnvPath -Encoding UTF8 -Force

# Claude 감지
function Test-ClaudeInstalled {
  $exe = Join-Path $env:LOCALAPPDATA "Programs\Claude\Claude.exe"
  $cfgDir = Join-Path $env:APPDATA "Claude"
  return (Test-Path $exe) -or (Test-Path $cfgDir)
}
function Get-ClaudeConfigPath { Join-Path $env:APPDATA "Claude\claude_desktop_config.json" }

if (-not (Test-ClaudeInstalled)) {
  if ($ClaudeRequired) {
    Write-Warning "Claude Desktop 미설치: 설치를 중단합니다."
    exit 2
  } else {
    Write-Warning "Claude Desktop 미설치: MCP 등록을 건너뜁니다."
    exit 0
  }
}

# MCP 등록
function Register-ClaudeMcpServer {
  param(
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$Command,
    [string[]]$Args = @(),
    [hashtable]$Env = @{}
  )
  $cfgPath = Get-ClaudeConfigPath
  $cfgDir  = Split-Path $cfgPath -Parent
  if (-not (Test-Path $cfgDir)) { New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null }

  $cfg = @{ mcpServers = @{} }
  if (Test-Path $cfgPath -and (Get-Item $cfgPath).Length -gt 0) {
    try {
      $cfg = (Get-Content -Raw $cfgPath | ConvertFrom-Json -AsHashtable)
      if (-not $cfg.ContainsKey("mcpServers")) { $cfg["mcpServers"] = @{} }
    } catch {
      Write-Warning "기존 설정을 읽을 수 없어 초기화합니다: $cfgPath"
      $cfg = @{ mcpServers = @{} }
    }
  }

  $cfg["mcpServers"][$Name] = @{
    command = $Command
    args    = $Args
    env     = $Env
  }

  Copy-Item $cfgPath "$cfgPath.bak-$(Get-Date -Format yyyyMMddHHmmss)" -ErrorAction SilentlyContinue
  ($cfg | ConvertTo-Json -Depth 10) | Set-Content -Path $cfgPath -Encoding UTF8
  Write-Host "Claude MCP 서버 등록 완료: $Name"
}

$ExePath = Join-Path $AppDir "NAS-Scanner.exe"
$envMap = @{
  ENV_PATH = $EnvPath
  SCAN_ROOT = $ScanRoot
  INDEX_DB  = $IndexDb
}
Register-ClaudeMcpServer -Name "filescan-preview-nas-db" -Command $ExePath -Env $envMap

Write-Host "설정 완료. Claude Desktop을 재시작하면 도구가 보입니다."
exit 0
