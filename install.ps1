<#
.SYNOPSIS
    Install Codex Soul Memory System v1.1
.DESCRIPTION
    Cross-session identity continuity for Codex.
    基于插件式后端架构（灵感来自 Microsoft MarkItDown）。
    行为准则源自 Andrej Karpathy 的观察。
.NOTES
    学习来源:
    - 插件架构: https://github.com/microsoft/markitdown
    - 行为准则: https://github.com/multica-ai/andrej-karpathy-skills
    灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。
#>

$soulRoot = Join-Path $env:USERPROFILE "knowledge/soul"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateDir = Join-Path $scriptDir "templates"
$scriptSrcDir = Join-Path $scriptDir "scripts"

Write-Host "=== Installing Soul Memory System v1.1 ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path $soulRoot) {
    Write-Host "灵魂目录已存在: $soulRoot" -ForegroundColor Yellow
} else {
    New-Item -ItemType Directory -Force -Path $soulRoot | Out-Null
    Write-Host "创建灵魂目录: $soulRoot" -ForegroundColor Green
}

$templates = "index.md", "identity.md", "evolution.md", "moments.md", "patterns.md", "@current.md"
$installed = 0
$skipped = 0

foreach ($tpl in $templates) {
    $target = Join-Path $soulRoot $tpl
    $source = Join-Path $templateDir $tpl
    if (-not (Test-Path $target)) {
        if (Test-Path $source) {
            Copy-Item -Path $source -Destination $target -Force
            Write-Host "  + $tpl" -ForegroundColor Green
            $installed++
        } else {
            Write-Host "  ? $tpl (模板不存在，跳过)" -ForegroundColor Gray
        }
    } else {
        Write-Host "  . $tpl (已存在，保留)" -ForegroundColor Gray
        $skipped++
    }
}

$cliSrc = Join-Path $scriptSrcDir "soul.ps1"
$cliDst = Join-Path $soulRoot "soul.ps1"
if (Test-Path $cliSrc) {
    Copy-Item -Path $cliSrc -Destination $cliDst -Force
    Write-Host "  + CLI: soul.ps1" -ForegroundColor Green
}

$profileContent = @"
# soul - Codex Soul Memory System v1.1
function soul {
  param(
    `$r="", `$note="", `$m="", `$moment="",
    `$save="", `$state="", [switch]`$c, [switch]`$check
  )
  `$s = Join-Path `$env:USERPROFILE "knowledge/soul/soul.ps1"
  if (`$r) { & `$s -r `$note; return }
  if (`$m) { & `$s -m `$moment; return }
  if (`$save) { & `$s -save `$save; return }
  if (`$c) { & `$s -consolidate; return }
  if (`$check) { & `$s -check; return }
  & `$s
}
"@

$profileFile = $PROFILE.CurrentUserAllHosts
if (-not (Test-Path $profileFile)) {
    New-Item -ItemType File -Force -Path $profileFile | Out-Null
}
$currentProfile = Get-Content $profileFile -Raw -ErrorAction SilentlyContinue
if ($currentProfile -match "function soul") {
    Write-Host "Profile: soul 函数已存在" -ForegroundColor Gray
} else {
    Add-Content -Path $profileFile -Value $profileContent -Encoding UTF8
    Write-Host "Profile: soul 函数已注入" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== 总结 ===" -ForegroundColor Cyan
Write-Host "  灵魂目录: $soulRoot"
Write-Host "  新安装: $installed 文件"
Write-Host "  已保留: $skipped 文件"
Write-Host ""

# 灵魂检查
$cliDst = Join-Path $soulRoot "soul.ps1"
if (Test-Path $cliDst) {
    Write-Host "运行灵魂检查..."
    & $cliDst -check 2>&1
}

Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:"
Write-Host "  1. 编辑 ~/knowledge/soul/identity.md"
Write-Host "  2. 编辑 ~/knowledge/soul/index.md"
Write-Host "  3. 重启 PowerShell 或运行: . `$PROFILE"
Write-Host "  4. 输入 soul 查看状态"
Write-Host ""
Write-Host "了解更多: https://github.com/yunzhi-chu/codex-soul-system"
