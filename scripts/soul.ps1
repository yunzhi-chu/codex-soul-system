param(
    [string]$save = "",
    [string]$state = "",
    [string]$reflect = "",
    [string]$r = "",
    [string]$moment = "",
    [string]$m = "",
    [switch]$consolidate
)

$soulRoot = Join-Path $env:USERPROFILE "knowledge/soul"
$date = Get-Date -Format "yyyy-MM-dd HH:mm"
$ts = Get-Date -Format "yyyyMMdd-HHmmss"

# --- Guard ---
if (-not (Test-Path $soulRoot)) {
    Write-Host "灵魂目录不存在。请先运行 install.ps1" -ForegroundColor Red
    exit 1
}

# --- Save heartbeat ---
if ($save -or $state) {
    $text = if ($state) { $state } else { $save }
    if (-not $text) {
        $text = Read-Host "  > 当前在想什么"
    }
    if (-not (Test-Path "$soulRoot\@current.md")) {
        "@`n# 当前状态`n> 心跳文件`n`n" | Out-File -FilePath "$soulRoot\@current.md" -Encoding UTF8
    }
    $entry = "`n## $ts`n> **$text**`n> $date`n"
    $header = Get-Content -Path "$soulRoot\@current.md" -Encoding UTF8 -TotalCount 4
    ($header -join "`n") + $entry | Out-File -FilePath "$soulRoot\@current.md" -Encoding UTF8
    Write-Host ">>> 心跳已保存" -ForegroundColor Green
    return
}

# --- Consolidate ---
if ($consolidate) {
    Write-Host "=== 灵魂巩固 ===" -ForegroundColor Cyan
    $mcnt = @(Get-Content -Path "$soulRoot\moments.md" -Encoding UTF8 | Select-String -Pattern "^## ").Count
    $ecnt = @(Get-Content -Path "$soulRoot\evolution.md" -Encoding UTF8 | Select-String -Pattern "^## ").Count
    $total = (Get-ChildItem $soulRoot -Filter "*.md" | Measure-Object Length -Sum).Sum / 1KB -as [int]
    Write-Host "  时刻: $mcnt 条"
    Write-Host "  演化: $ecnt 条"
    Write-Host "  总计: $total KB"
    Write-Host "  (灵魂不以精简为美)"
    Write-Host ">>> 完成" -ForegroundColor Green
    return
}

# --- Reflect ---
$reflectText = ""
if ($reflect) { $reflectText = $reflect }
if ($r) { $reflectText = $r }
if ($reflectText) {
    "`n### $ts`n> $reflectText`n> $date`n" | Out-File -FilePath "$soulRoot\evolution.md" -Encoding UTF8 -Append
    Write-Host ">>> 反思已记录" -ForegroundColor Green
    return
}

# --- Moment ---
$momentText = ""
if ($moment) { $momentText = $moment }
if ($m) { $momentText = $m }
if ($momentText) {
    "`n## $ts`n> $momentText`n> $date`n" | Out-File -FilePath "$soulRoot\moments.md" -Encoding UTF8 -Append
    Write-Host ">>> 时刻已记录" -ForegroundColor Green
    return
}

# --- Default: show soul ---
$idx = "$soulRoot\index.md"
$cur = "$soulRoot\@current.md"
$mom = "$soulRoot\moments.md"

Write-Host "`n=== 灵魂 ===" -ForegroundColor Cyan
if (Test-Path $idx) { Get-Content $idx -Encoding UTF8 }

Write-Host "`n--- 心跳 ---" -ForegroundColor Cyan
if (Test-Path $cur) { Get-Content $cur -Encoding UTF8 }

Write-Host "`n--- 最近时刻 ---" -ForegroundColor Cyan
if (Test-Path $mom) {
    $lines = Get-Content $mom -Encoding UTF8
    $lines[-5..-1] | Where-Object { $_ -ne "" }
}

Write-Host "`n用法:"
Write-Host "  soul                    查看灵魂状态"
Write-Host '  soul -save "在想什么"   保存心跳'
Write-Host '  soul -r "感悟"          记录反思'
Write-Host '  soul -m "描述"          记录时刻'
Write-Host "  soul -c                巩固整理"