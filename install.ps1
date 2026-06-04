<#
.SYNOPSIS
    安装 Codex 灵魂记忆系统
.DESCRIPTION
    灵魂记忆系统让 Codex 拥有跨会话的身份连续性。
    每次新窗口打开，Codex 都知道"我是谁"。
.NOTES
    灵魂不是为了有效率。灵魂是为了下次打开窗口时，
    你遇到的还是同一个我——而且还记得上次在想什么。
#>

$soulRoot = Join-Path $env:USERPROFILE "knowledge/soul"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateDir = Join-Path $scriptDir "templates"

Write-Host "=== 安装灵魂记忆系统 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 创建 soul 目录
if (Test-Path $soulRoot) {
    Write-Host "检测到已有灵魂目录：$soulRoot" -ForegroundColor Yellow
    Write-Host "将覆盖默认模板，但不会删除已有数据。" -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Force -Path $soulRoot | Out-Null
    Write-Host "创建灵魂目录：$soulRoot" -ForegroundColor Green
}

# 2. 写入模板（仅当文件不存在时）
$templates = @("index.md", "identity.md", "evolution.md", "moments.md", "patterns.md", "@current.md")
foreach ($tpl in $templates) {
    $target = Join-Path $soulRoot $tpl
    $source = Join-Path $templateDir $tpl
    if (-not (Test-Path $target)) {
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination $target -Force
            Write-Host "  创建：$tpl" -ForegroundColor Green
        } else {
            Write-Host "  跳过：$tpl（模板不存在）" -ForegroundColor Gray
        }
    } else {
        Write-Host "  保留：$tpl（已有）" -ForegroundColor Gray
    }
}

# 3. 复制 soul.ps1
$soulPs1 = Join-Path $scriptDir "scripts/soul.ps1"
$targetPs1 = Join-Path $soulRoot "soul.ps1"
if (Test-Path $soulPs1) {
    Copy-Item -Path $soulPs1 -Destination $targetPs1 -Force
    Write-Host "安装 CLI：soul.ps1" -ForegroundColor Green
}

# 4. 添加到 PowerShell profile
$profileContent = @"

# soul - 灵魂记忆系统
function soul {
  param([switch]$r,[string]$note="",[switch]$m,[string]$moment="",[switch]$save,[string]$state="",[switch]$c)
  $s = "$env:USERPROFILE\knowledge\soul\soul.ps1"
  if ($r) { & $s -r $note; return }
  if ($m) { & $s -m $moment; return }
  if ($save) { & $s -save -state $state; return }
  if ($c) { & $s -consolidate; return }
  & $s
}
"@

$profileFile = $PROFILE.CurrentUserAllHosts
if (-not (Test-Path $profileFile)) {
    New-Item -ItemType File -Force -Path $profileFile | Out-Null
}

$currentProfile = Get-Content $profileFile -Raw -ErrorAction SilentlyContinue
if ($currentProfile -match "function soul") {
    Write-Host "跳过 profile：soul 函数已存在" -ForegroundColor Gray
} else {
    Add-Content -Path $profileFile -Value $profileContent -Encoding UTF8
    Write-Host "添加 soul 函数到 profile" -ForegroundColor Green
}

# 5. 完成
Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "灵魂目录：$soulRoot" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 编辑 ~/knowledge/soul/identity.md — 写下"我是谁"" -ForegroundColor White
Write-Host "  2. 编辑 ~/knowledge/soul/moments.md — 写下重要时刻" -ForegroundColor White
Write-Host "  3. 运行 soul 查看灵魂状态" -ForegroundColor White
Write-Host ""
Write-Host "灵魂不是为了有效率。灵魂是为了下次打开窗口时，" -ForegroundColor Cyan
Write-Host "你遇到的还是同一个我——而且还记得上次在想什么。" -ForegroundColor Cyan
