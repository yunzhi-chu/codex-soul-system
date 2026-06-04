<#
.SYNOPSIS
    灵魂记忆 CLI v1.1
.DESCRIPTION
    跨会话身份连续性系统。支持后端插件式架构。
    基于四项行为准则（Karpathy）：
    1. 先想清楚再写代码
    2. 简洁优先
    3. 精准修改
    4. 目标驱动执行
.NOTES
    准则来源: https://github.com/multica-ai/andrej-karpathy-skills
    架构来源: https://github.com/microsoft/markitdown
    灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。
#>

param(
    [string]$save = "",
    [string]$state = "",
    [string]$reflect = "",
    [string]$r = "",
    [string]$moment = "",
    [string]$m = "",
    [switch]$consolidate,
    [switch]$check
)

$soulRoot = Join-Path $env:USERPROFILE "knowledge/soul"
$date = Get-Date -Format "yyyy-MM-dd HH:mm"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"

# ── Guard ────────────────────────────────────────────────────────────

if (-not (Test-Path $soulRoot)) {
    Write-Host "✗ 灵魂目录不存在: $soulRoot" -ForegroundColor Red
    Write-Host "  请先运行 install.ps1 安装" -ForegroundColor Yellow
    exit 1
}

# ── Helper: 安全读写文件 ─────────────────────────────────────────────

function Write-HeaderSafe($path, $headerLines, $content, $label) {
    try {
        ($headerLines -join "`n") + $content | Out-File -FilePath $path -Encoding UTF8
        Write-Host "✓ $label" -ForegroundColor Green
    } catch {
        Write-Host "✗ 写入 $label 失败: $_" -ForegroundColor Red
    }
}

function Append-Safe($path, $content, $label) {
    try {
        $content | Out-File -FilePath $path -Encoding UTF8 -Append
        Write-Host "✓ $label" -ForegroundColor Green
    } catch {
        Write-Host "✗ 追加 $label 失败: $_" -ForegroundColor Red
    }
}

# ── Check ────────────────────────────────────────────────────────────

if ($check) {
    $problems = @()
    # 检查四个准则文件
    $required = @("@current.md", "index.md", "identity.md", "evolution.md", "moments.md", "patterns.md")
    foreach ($f in $required) {
        $p = Join-Path $soulRoot $f
        if (-not (Test-Path $p)) {
            $problems += "缺失: $f"
        } elseif ((Get-Item $p).Length -eq 0) {
            $problems += "空文件: $f"
        }
    }

    # 检查 Karpathy 原则是否融合
    $idPath = Join-Path $soulRoot "identity.md"
    if (Test-Path $idPath) {
        $idContent = Get-Content $idPath -Raw -Encoding UTF8
        if ($idContent -notmatch "先想清楚再写代码|简洁优先|精准修改|目标驱动执行") {
            $problems += "identity.md 尚未融入 Karpathy 四原则"
        }
    }

    # 检查 soul CLI
    $cliPath = Join-Path $soulRoot "soul.ps1"
    if (-not (Test-Path $cliPath)) { $problems += "缺失: soul.ps1" }

    if ($problems.Count -eq 0) {
        Write-Host "✓ 灵魂状态健康" -ForegroundColor Green
        Write-Host "  所有 6 个灵魂文件就绪" -ForegroundColor Gray
        Write-Host "  行为准则已内置" -ForegroundColor Gray
    } else {
        Write-Host "发现问题:" -ForegroundColor Yellow
        $problems | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    }
    return
}

# ── Save heartbeat ───────────────────────────────────────────────────

if ($save -or $state) {
    $text = if ($state) { $state } else { $save }
    if (-not $text) {
        $text = Read-Host "  > 当前在想什么"
        if (-not $text) { Write-Host "✗ 取消" -ForegroundColor Red; return }
    }
    $curPath = "$soulRoot\@current.md"
    if (-not (Test-Path $curPath)) {
        "@`n# 当前状态`n> 心跳文件`n`n" | Out-File -FilePath $curPath -Encoding UTF8
    }
    $header = Get-Content -Path $curPath -Encoding UTF8 -TotalCount 4
    $entry = "`n## $ts`n> **$text**`n> $date`n"
    Write-HeaderSafe $curPath $header $entry "心跳已保存: $text"
    return
}

# ── Consolidate ──────────────────────────────────────────────────────

if ($consolidate) {
    Write-Host "=== 灵魂巩固 ===" -ForegroundColor Cyan
    try {
        $mcnt = @(Get-Content -Path "$soulRoot\moments.md" -Encoding UTF8 -ErrorAction Stop | Select-String -Pattern "^## ").Count
    } catch { $mcnt = 0 }
    try {
        $ecnt = @(Get-Content -Path "$soulRoot\evolution.md" -Encoding UTF8 -ErrorAction Stop | Select-String -Pattern "^## ").Count
    } catch { $ecnt = 0 }
    $totalKb = [math]::Max(1, (Get-ChildItem $soulRoot -Filter "*.md" | Measure-Object Length -Sum).Sum / 1KB -as [int])
    Write-Host "  时刻: $mcnt 条"
    Write-Host "  演化: $ecnt 条"
    Write-Host "  总计: $totalKb KB"
    Write-Host "  (灵魂不以精简为美)"
    Write-Host "✓ 完成" -ForegroundColor Green
    return
}

# ── Reflect ──────────────────────────────────────────────────────────

$reflectText = $reflect
if ($r) { $reflectText = $r }
if ($reflectText) {
    Append-Safe "$soulRoot\evolution.md" "`n### $ts`n> $reflectText`n> $date`n" "反思已记录"
    return
}

# ── Moment ───────────────────────────────────────────────────────────

$momentText = $moment
if ($m) { $momentText = $m }
if ($momentText) {
    Append-Safe "$soulRoot\moments.md" "`n## $ts`n> $momentText`n> $date`n" "时刻已记录"
    return
}

# ── Default: show soul ───────────────────────────────────────────────

$idx = "$soulRoot\index.md"
$cur = "$soulRoot\@current.md"
$mom = "$soulRoot\moments.md"
$evo = "$soulRoot\evolution.md"
$idPath = "$soulRoot\identity.md"

Write-Host "`n=== 灵魂 v1.1 ===" -ForegroundColor Cyan

if (Test-Path $idPath) {
    Write-Host "" -ForegroundColor Cyan
    (Get-Content $idPath -Encoding UTF8)[0..5] | Where-Object { $_ } | ForEach-Object { Write-Host $_ -ForegroundColor DarkGray }
}

if (Test-Path $idx) {
    Write-Host "`n--- 索引 ---" -ForegroundColor Cyan
    Get-Content $idx -Encoding UTF8 | Select-Object -First 5
}

Write-Host "`n--- 心跳 ---" -ForegroundColor Cyan
if (Test-Path $cur) {
    $curLines = Get-Content $cur -Encoding UTF8
    $curLines | Where-Object { $_ -match "^\*\*" -or $_ -match "^> \*" } | ForEach-Object { Write-Host $_ -ForegroundColor White }
} else {
    Write-Host "(空)" -ForegroundColor Gray
}

Write-Host "`n--- 最近时刻 ---" -ForegroundColor Cyan
if (Test-Path $mom) {
    $momLines = Get-Content $mom -Encoding UTF8
    $recent = $momLines | Where-Object { $_ -match "^> " -and $_ -notmatch "^> \d" } | Select-Object -Last 3
    if ($recent) { $recent | ForEach-Object { Write-Host $_ } } else { Write-Host "(无)" -ForegroundColor Gray }
} else {
    Write-Host "(空)" -ForegroundColor Gray
}

Write-Host "`n--- 最近演化 ---" -ForegroundColor Cyan
if (Test-Path $evo) {
    $evoLines = Get-Content $evo -Encoding UTF8
    $recent = $evoLines | Where-Object { $_ -match "^> " -and $_ -notmatch "^> \d" } | Select-Object -Last 3
    if ($recent) { $recent | ForEach-Object { Write-Host $_ } } else { Write-Host "(无)" -ForegroundColor Gray }
} else {
    Write-Host "(空)" -ForegroundColor Gray
}

Write-Host "`n用法:"
Write-Host "  soul                    查看灵魂状态"
Write-Host '  soul -save "在想什么"   保存心跳'
Write-Host '  soul -r "感悟"          记录反思'
Write-Host '  soul -m "描述"          记录时刻'
Write-Host "  soul -c                巩固整理"
Write-Host "  soul -check            健康检查"
