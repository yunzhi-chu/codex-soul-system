<#
.SYNOPSIS
    灵魂记忆 CLI v1.3
.DESCRIPTION
    跨会话身份连续性系统。支持 SQLite + 文件双后端。
    基于四项行为准则（Karpathy）：
    1. 先想清楚再写代码
    2. 简洁优先
    3. 精准修改
    4. 目标驱动执行
.NOTES
    准则来源: https://github.com/multica-ai/andrej-karpathy-skills
    架构来源: https://github.com/microsoft/markitdown
    结构化记忆: https://github.com/thedotmack/claude-mem
    灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。
#>

param(
    [string] = "",
    [string] = "",
    [string] = "",
    [string] = "",
    [string] = "",
    [string] = "",
    [switch],
    [switch]
)

 = Join-Path C:\Users\Administrator "knowledge/soul"
 = Get-Date -Format "yyyy-MM-dd HH:mm"
 = Get-Date -Format "yyyyMMdd-HHmmss"

# --- Guard -------------------------------------------------

if (-not (Test-Path )) {
    Write-Host "✗ 灵魂目录不存在: " -ForegroundColor Red
    Write-Host "  请先运行 install.ps1 安装" -ForegroundColor Yellow
    exit 1
}

# --- Helper ------------------------------------------------

function Write-HeaderSafe(C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11\outputs\codex-soul-system\scripts\soul.ps1, , , ) {
    try {
        ( -join "
") +  | Out-File -FilePath C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11\outputs\codex-soul-system\scripts\soul.ps1 -Encoding UTF8
        Write-Host "✓ " -ForegroundColor Green
    } catch {
        Write-Host "✗ 写入  失败: " -ForegroundColor Red
    }
}

function Append-Safe(C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11\outputs\codex-soul-system\scripts\soul.ps1, , ) {
    try {
         | Out-File -FilePath C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11\outputs\codex-soul-system\scripts\soul.ps1 -Encoding UTF8 -Append
        Write-Host "✓ " -ForegroundColor Green
    } catch {
        Write-Host "✗ 追加  失败: " -ForegroundColor Red
    }
}

# --- Check -------------------------------------------------

if () {
     = @()
     = @("@current.md", "index.md", "identity.md", "evolution.md", "moments.md", "patterns.md")
    foreach ( in ) {
         = Join-Path  
        if (-not (Test-Path )) {
             += "缺失: "
        } elseif ((Get-Item ).Length -eq 0) {
             += "空文件: "
        }
    }

    # 检查 SQLite 数据库
     = Join-Path  ".soul.db"
    if (Test-Path ) {
        Write-Host "  ✓ SQLite 数据库存在" -ForegroundColor Green
         = (Get-Item ).Length / 1KB
        Write-Host "    数据库大小: 0 KB" -ForegroundColor Gray
    }

    # 检查 Karpathy 原则
     = Join-Path  "identity.md"
    if (Test-Path ) {
         = Get-Content  -Raw -Encoding UTF8
        if ( -notmatch "先想清楚再写代码|简洁优先|精准修改|目标驱动执行") {
             += "identity.md 尚未融入 Karpathy 四原则"
        }
    }

     = Join-Path  "soul.ps1"
    if (-not (Test-Path )) {  += "缺失: soul.ps1" }

    if (.Count -eq 0) {
        Write-Host "✓ 灵魂状态健康" -ForegroundColor Green
        Write-Host "  所有 6 个灵魂文件就绪" -ForegroundColor Gray
        Write-Host "  行为准则已内置" -ForegroundColor Gray
        if (Test-Path ) { Write-Host "  SQLite 数据库就绪" -ForegroundColor Gray }
    } else {
        Write-Host "发现问题:" -ForegroundColor Yellow
         | ForEach-Object { Write-Host "  " -ForegroundColor Yellow }
    }
    return
}

# --- Save heartbeat ----------------------------------------

if ( -or ) {
     = if () {  } else {  }
    if (-not ) {
         = Read-Host "  > 当前在想什么"
        if (-not ) { Write-Host "✗ 取消" -ForegroundColor Red; return }
    }
     = "\@current.md"
    if (-not (Test-Path )) {
        "@
# 当前状态
> 心跳文件

" | Out-File -FilePath  -Encoding UTF8
    }
     = Get-Content -Path  -Encoding UTF8 -TotalCount 4
     = "
## 
> ****
> 
"
    Write-HeaderSafe    "心跳已保存: "
    return
}

# --- Consolidate -------------------------------------------

if () {
    Write-Host "=== 灵魂巩固 ===" -ForegroundColor Cyan
    try {
         = @(Get-Content -Path "\moments.md" -Encoding UTF8 -ErrorAction Stop | Select-String -Pattern "^## ").Count
    } catch {  = 0 }
    try {
         = @(Get-Content -Path "\evolution.md" -Encoding UTF8 -ErrorAction Stop | Select-String -Pattern "^## ").Count
    } catch {  = 0 }

     = "\.soul.db"
    if (Test-Path ) {
         = [math]::Max(1, (Get-Item ).Length / 1KB -as [int])
        Write-Host "  SQLite 数据库:  KB" -ForegroundColor Gray
    }

     = [math]::Max(1, (Get-ChildItem  -Filter "*.md" | Measure-Object Length -Sum).Sum / 1KB -as [int])
    Write-Host "  时刻:  条"
    Write-Host "  演化:  条"
    Write-Host "  文件:  KB"
    Write-Host "  (灵魂不以精简为美)"
    Write-Host "✓ 完成" -ForegroundColor Green
    return
}

# --- Reflect -----------------------------------------------

 = 
if () {  =  }
if () {
    Append-Safe "\evolution.md" "
### 
> 
> 
" "反思已记录"
    return
}

# --- Moment ------------------------------------------------

 = 
if () {  =  }
if () {
    Append-Safe "\moments.md" "
## 
> 
> 
" "时刻已记录"
    return
}

# --- Default: show soul ------------------------------------

 = "\index.md"
 = "\@current.md"
 = "\moments.md"
 = "\evolution.md"
 = "\identity.md"
 = "\.soul.db"

Write-Host "
=== 灵魂 v1.3 ===" -ForegroundColor Cyan

if (Test-Path ) {
    Write-Host "" -ForegroundColor Cyan
    (Get-Content  -Encoding UTF8)[0..5] | Where-Object {  } | ForEach-Object { Write-Host  -ForegroundColor DarkGray }
}

if (Test-Path ) {
    Write-Host "
--- 索引 ---" -ForegroundColor Cyan
    Get-Content  -Encoding UTF8 | Select-Object -First 5
}

Write-Host "
--- 心跳 ---" -ForegroundColor Cyan
if (Test-Path ) {
     = Get-Content  -Encoding UTF8
     | Where-Object {  -match "^\*\*" -or  -match "^> \*" } | ForEach-Object { Write-Host  -ForegroundColor White }
} else {
    Write-Host "(空)" -ForegroundColor Gray
}

Write-Host "
--- 最近时刻 ---" -ForegroundColor Cyan
if (Test-Path ) {
     = Get-Content  -Encoding UTF8
     =  | Where-Object {  -match "^> " -and  -notmatch "^> \d" } | Select-Object -Last 3
    if () {  | ForEach-Object { Write-Host  } } else { Write-Host "(无)" -ForegroundColor Gray }
} else {
    Write-Host "(空)" -ForegroundColor Gray
}

Write-Host "
--- 最近演化 ---" -ForegroundColor Cyan
if (Test-Path ) {
     = Get-Content  -Encoding UTF8
     =  | Where-Object {  -match "^> " -and  -notmatch "^> \d" } | Select-Object -Last 3
    if () {  | ForEach-Object { Write-Host  } } else { Write-Host "(无)" -ForegroundColor Gray }
} else {
    Write-Host "(空)" -ForegroundColor Gray
}

if (Test-Path ) {
     = [math]::Round((Get-Item ).Length / 1KB, 1)
    Write-Host "
--- 存储 ---" -ForegroundColor Cyan
    Write-Host "  SQLite 数据库:  KB" -ForegroundColor Gray
}

Write-Host "
用法:"
Write-Host "  soul                    查看灵魂状态"
Write-Host '  soul -save "在想什么"   保存心跳'
Write-Host '  soul -r "感悟"          记录反思'
Write-Host '  soul -m "描述"          记录时刻'
Write-Host "  soul -c                巩固整理"
Write-Host "  soul -health            健康检查"
