param(
  [string]$AppDir  = "C:\Program Files\GenAILabs\NAS-NoDB-Scanner",
  [string]$DataDir = "C:\ProgramData\GenAILabs\NAS-NoDB-Scanner",
  [switch]$RemoveData,
  [switch]$RemoveClaude
)

$ErrorActionPreference = "Stop"
Write-Host "=== NAS-NoDB-Scanner 언인스톨 시작 ==="

if (Test-Path $AppDir) {
  try { Remove-Item $AppDir -Recurse -Force; Write-Host "삭제: $AppDir" } catch { Write-Warning $_ }
}
if ($RemoveData -and (Test-Path $DataDir)) {
  try { Remove-Item $DataDir -Recurse -Force; Write-Host "삭제: $DataDir" } catch { Write-Warning $_ }
}

if ($RemoveClaude) {
  $cfgPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
  if (Test-Path $cfgPath) {
    try {
      $cfg = Get-Content -Raw $cfgPath | ConvertFrom-Json -AsHashtable
      if ($cfg.ContainsKey("mcpServers")) {
        $null = $cfg["mcpServers"].Remove("filescan-preview-nas-db")
        ($cfg | ConvertTo-Json -Depth 10) | Set-Content -Path $cfgPath -Encoding UTF8
        Write-Host "Claude MCP 서버 등록 제거 완료."
      }
    } catch { Write-Warning "Claude config 수정 실패: $_" }
  }
}
Write-Host "=== 언인스톨 완료 ==="
