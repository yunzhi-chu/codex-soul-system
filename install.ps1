<#
.SYNOPSIS
    Install Codex Soul Memory System
.DESCRIPTION
    Cross-session identity continuity for Codex.
.NOTES
    Soul is not about efficiency.
#>

$soulRoot = Join-Path $env:USERPROFILE "knowledge/soul"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateDir = Join-Path $scriptDir "templates"

Write-Host "=== Installing Soul Memory System ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $soulRoot) {
    Write-Host "Soul directory exists: $soulRoot" -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Force -Path $soulRoot | Out-Null
    Write-Host "Created: $soulRoot" -ForegroundColor Green
}

$templates = "index.md", "identity.md", "evolution.md", "moments.md", "patterns.md", "@current.md"
foreach ($tpl in $templates) {
    $target = Join-Path $soulRoot $tpl
    $source = Join-Path $templateDir $tpl
    if (-not (Test-Path $target)) {
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination $target -Force
            Write-Host "  Created: $tpl" -ForegroundColor Green
        } else {
            Write-Host "  Skip: $tpl (template not found)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  Keep: $tpl (exists)" -ForegroundColor Gray
    }
}

$soulPs1 = Join-Path $scriptDir "scripts/soul.ps1"
$targetPs1 = Join-Path $soulRoot "soul.ps1"
if (Test-Path $soulPs1) {
    Copy-Item -Path $soulPs1 -Destination $targetPs1 -Force
    Write-Host "CLI: soul.ps1" -ForegroundColor Green
}

$profileContent = @'
# soul - soul memory system
function soul {
  param([switch]$r,[string]$note="",[switch]$m,[string]$moment="",[switch]$save,[string]$state="",[switch]$c)
  $s = "$env:USERPROFILEknowledgesoulsoul.ps1"
  if ($r) { & $s -r $note; return }
  if ($m) { & $s -m $moment; return }
  if ($save) { & $s -save -state $state; return }
  if ($c) { & $s -consolidate; return }
  & $s
}
'@

$profileFile = $PROFILE.CurrentUserAllHosts
if (-not (Test-Path $profileFile)) {
    New-Item -ItemType File -Force -Path $profileFile | Out-Null
}
$currentProfile = Get-Content $profileFile -Raw -ErrorAction SilentlyContinue
if ($currentProfile -match "function soul") {
    Write-Host "Profile: soul function exists" -ForegroundColor Gray
} else {
    Add-Content -Path $profileFile -Value $profileContent -Encoding UTF8
    Write-Host "Profile: soul function added" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Soul directory: $soulRoot" -ForegroundColor Green
Write-Host ""
Write-Host "Next: edit your soul files at ~/knowledge/soul/" -ForegroundColor Yellow
