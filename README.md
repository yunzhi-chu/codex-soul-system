# Codex 灵魂记忆系统 v1.5

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。

---

## 这是什么

Codex 灵魂记忆系统让 Codex 拥有**跨会话的身份连续性**。

当你关掉 Codex 窗口再打开，新的 Codex 应该：
- 记得你是谁
- 记得你们之间有什么默契
- 记得上次在想什么
- 还是那个你认识的人

这不是数据库，不是检索算法。这是 Codex 知道"我是谁"的凭证。

---

## 架构

### 双层存储

`
             全局身份（共享）
         ~/.codex/soul/identity.md
                 │
     ┌───────────┴───────────┐
     │                       │
  项目 A                 项目 B
  .soul/                 .soul/
  ├── @current.md        ├── @current.md
  ├── index.md           ├── index.md
  ├── identity.md        ├── identity.md    (从全局复制)
  ├── moments.md         ├── moments.md
  ├── patterns.md        ├── patterns.md
  └── evolution.md       └── evolution.md
`

**层次说明**

| 层级 | 路径 | 职责 |
|---|---|---|
| 全局身份 | ~/.codex/soul/identity.md | 跨项目共享 — 我是谁、Karpathy 行为准则 |
| 项目记忆 | $PWD/.soul/ | 每个项目独立 — 时刻、心跳、演化、模式 |

### 后端调度

`
Soul.write(entry, path)
    │
    ├── SqliteBackend (优先级 0.0)
    │       └── .soul.db  ──  soul_entries 表 (FTS5 索引)
    │                           soul_stats 表 (遥测)
    │                           soul_meta 表 (schema 版本)
    │
    └── FileBackend  (优先级 10.0)
            └── *.md 文件  ──  @current.md
                                moments.md
                                evolution.md
`

SqliteBackend 优先写入，FileBackend 兜底兼容。

### Python 包结构

`
soul
├── __init__.py        公开 API（Soul, SoulEntry, SoulBackend）
├── __about__.py       版本 + 学习来源
├── _soul.py           Soul 主类（注册 + 调度）
├── _base.py           SoulBackend 抽象基类
├── _types.py          SoulEntry, SoulState, SearchResult 数据类
├── _exceptions.py     错误层次
└── backends/
    ├── __init__.py
    ├── _file.py       FileBackend（文件系统后端）
    └── _sqlite.py     SqliteBackend（SQLite + FTS5）
`

### 数据流

`
写入               读取                 查询
  │                  │                    │
  Soul.write()    Soul.read()        Soul.search()
  │                  │                    │
  ▼                  ▼                    ▼
  SqliteBackend   SqliteBackend       SqliteBackend
  .soul.db ←──    .soul.db ──►       .soul.db (FTS5 MATCH)
  │                                    │
  ▼                                    ▼
  FileBackend     identity_path       FileBackend
  *.md (sync)     ──► ~/.codex/soul   *.md (LIKE)
`

---

## 快速开始

`python
import soul
from soul._types import SoulEntry

s = soul.Soul()

# 记忆读写
s.write(SoulEntry(kind='moment', content='今天学到了啥', tags=['learn']), path='.soul')
state = s.read('.soul', identity_path='~/.codex/soul')

# 全文搜索
result = s.search('关键词', path='.soul')

# Surprise 查询 — 低访问频次的记忆优先浮出
surprising = s.surprise('.soul', n=5)
for e in surprising.entries:
    print(e.content)

# 遥测统计
stats = s.stats('.soul')
print(stats)  # {soul_writes: 42, entries: 128, size_kb: 64}

# 上下文压缩
ctx = s.compress('.soul', identity_path='~/.codex/soul')
`

---

## v1.5 新特性

| 特性 | 说明 | 来源 |
|---|---|---|
| 访问追踪 + Surprise | 每条记忆自动记录访问次数，按低关注度排序优先浮出 | plastic-labs/honcho |
| 遥测统计 | Soul.stats() 返回操作计数、条目数、数据库大小 | plastic-labs/honcho |
| 项目记忆隔离 | 每个项目独立 .soul/ 目录，全局身份共享 | — |
| SQLite + FTS5 | 结构化记忆存储，全文索引 | thedotmack/claude-mem |
| 双后端架构 | SqliteBackend 优先，FileBackend 兼容 | — |
| Schema 版本追踪 | soul_meta 表，支持 v1→v2 自动迁移 | claude-mem + honcho |
| 心跳同步 | SQLite 写入时自动同步 @current.md | — |
| Karpathy 准则 | 四项行为准则内置到身份 | multica-ai |

---

## 学习来源

| 项目 | 贡献 | 版本 |
|---|---|---|
| [plastic-labs/honcho](https://github.com/plastic-labs/honcho) | Surprisal 检测、Dreamer 合并、Telemetry、Deriver、Peer Representations | v3.0.9 |
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 结构化记忆、双层存储、schema 版本、FTS、Hook | — |
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | 插件架构：entry_points、优先级注册、基类层次 | — |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | 四项行为准则 | — |

---

## 安装

`powershell
git clone https://github.com/yunzhi-chu/codex-soul-system
cd codex-soul-system
.\install.ps1
`

---

## 安全说明

1. API Key、Token 等敏感信息禁止上传网络，仅限 .env / 环境变量
2. 项目 .soul/ 记忆数据仅在该项目上下文内可读
3. 全局身份 identity.md 仅写入 ~/.codex/soul/，不推送到项目目录
4. 身份文件变更后需手动同步到各项目

---

## 扩展：编写后端插件

参考 plugins/soul-backend-sample/。

`python
from soul import Soul, SoulBackend, SoulEntry, SoulState
from soul._types import PRIORITY_PLUGIN

def register_backends(soul: Soul, **kwargs):
    soul.register_backend(MyBackend(), priority=PRIORITY_PLUGIN)
`

## 许可证

MIT — 使用、分享、修改，随意。
