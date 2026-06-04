<#
.SYNOPSIS
    Soul Hook — 自动捕捉会话上下文到灵魂记忆
.DESCRIPTION
    在会话结束时自动保存心跳、最近文件和重要决定到 soul。
    灵感: claude-mem 的 Hook 自动捕获模式。
.NOTES
    用法: powershell -NoProfile -File soul-hook.ps1 -SessionEnd
#>

param(
    [switch]$SessionEnd,
    [string]$File = "",
    [string]$Decision = ""
)

$soulRoot = Join-Path $env:USERPROFILE "knowledge/soul"
$soulCli = Join-Path $soulRoot "soul.ps1"
$date = Get-Date -Format "yyyy-MM-dd HH:mm"

if (-not (Test-Path $soulRoot)) { exit 0 }

# ── 会话结束时自动保存心跳 ──
if ($SessionEnd) {
    $cwd = (Get-Location).Path
    $heartbeat = "正在处理: $cwd"
    if (Test-Path $soulCli) { & $soulCli -save $heartbeat 2>&1 | Out-Null }
    exit 0
}

# ── 记录最近文件 ──
if ($File) {
    if (Test-Path $soulCli) {
        & $soulCli -m "处理文件: $File" 2>&1 | Out-Null
    }
    exit 0
}

# ── 记录重要决定 ──
if ($Decision) {
    if (Test-Path $soulCli) {
        & $soulCli -m "[decision] $Decision" 2>&1 | Out-Null
    }
    exit 0
}