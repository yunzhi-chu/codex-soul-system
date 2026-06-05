# Codex 灵魂记忆系统 v1.5

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。

## 这是什么

Codex 灵魂记忆系统让 Codex 拥有**跨会话的身份连续性**。

当你关掉 Codex 窗口再打开，新的 Codex 应该：
- 记得你是谁
- 记得你们之间有什么默契
- 记得上次在想什么
- 还是那个你认识的人

这不是数据库，不是检索算法。这是 Codex 知道"我是谁"的凭证。

## v1.5 新特性

- **访问追踪 + Surprise 查询** — 每条记忆自动记录访问次数，Soul.surprise() 按低关注度排序优先浮出（源自 plastic-labs/honcho Surprisal 检测）
- **遥测统计** — Soul.stats() 返回操作计数（writes、entries、size_kb），支持 token 经济决策（源自 plastic-labs/honcho telemetry）
- **项目记忆隔离** — 每个项目独立的 .soul/ 目录，全局身份共享（~/.codex/soul/identity.md）
- **SQLite 记忆后端** — 基于 SQLite + FTS5 的结构化记忆存储（源自 thedotmack/claude-mem）
- **FTS5 全文搜索** — 快速语义搜索，支持结构化字段（fact/concept/file）
- **双后端架构** — SqliteBackend 优先，FileBackend 向后兼容
- **Schema 版本追踪** — soul_meta 表记录 schema 版本，支持迁移
- **线程安全** — threading.local() 连接管理，支持 10 线程并发
- **心跳同步** — SQLite 写入时自动同步 @current.md
- **Codex 市场发布** — .codex-plugin/plugin.json 配置
- **行为准则内置** — Karpathy 四项原则已融入灵魂身份（identity.md）

## 架构

### 双层存储
`
~/.codex/soul/identity.md     全局身份（跨项目共享）
C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11/.soul/                     项目记忆（隔离）
    ├── @current.md              上次心跳
    ├── index.md                 项目索引
    ├── identity.md              项目副本（从全局复制）
    ├── moments.md               时刻记录
    ├── patterns.md              互动模式
    └── evolution.md             变化历程
`

### Python 包
`
soul/                               # 核心包
├── __init__.py                     # 公开 API
├── __about__.py                    # 版本 + 学习来源
├── _soul.py                        # Soul 主类
├── _base.py                        # SoulBackend 抽象基类
├── _types.py                       # SoulEntry, SoulState 数据类
├── _exceptions.py                  # 错误层次
└── backends/
    ├── __init__.py
    ├── _file.py                    # FileBackend（默认）
    └── _sqlite.py                  # SqliteBackend（SQLite + FTS5）
`

## API 快速参考

`python
import soul
from soul._types import SoulEntry

s = soul.Soul()

# 读写记忆
s.write(SoulEntry(kind='moment', content='今天学到了啥', tags=['learn']), path='.soul')
state = s.read('.soul', identity_path='~/.codex/soul')

# 搜索
result = s.search('关键词', path='.soul')

# 低访问频次记忆（Surprise）
surprising = s.surprise('.soul', n=5)
for e in surprising.entries:
    print(e.content)

# 遥测统计
stats = s.stats('.soul')
print(stats)  # {soul_writes: 42, entries: 128, size_kb: 64}

# 上下文压缩
ctx = s.compress('.soul', identity_path='~/.codex/soul')
`

## 学习来源

- **[plastic-labs/honcho](https://github.com/plastic-labs/honcho)** v3.0.9 — 记忆基础设施：Surprisal 检测、Deriver 异步实体提取、Dreamer 合并循环、Telemetry 操作追踪、Peer Representations
- **[thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)** — 结构化记忆（kind/facts/concepts/files）、双层存储（SQLite + Chroma）、schema 版本追踪、FTS 搜索、Hook 自动捕获
- **[microsoft/markitdown](https://github.com/microsoft/markitdown)** — 插件系统架构：entry_points 插件发现、ConverterRegistration 优先级注册模式、懒加载、基类层次
- **[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)** — 四项行为准则，由 Forrest Chang 整理为可复用 Codex Skill
- **Codex SDK** — 基于 SKILL.md + 文件系统的灵魂架构

## 安装

`powershell
git clone https://github.com/yunzhi-chu/codex-soul-system
cd codex-soul-system
.\install.ps1
`

## 安全说明

1. API Key、Token 等敏感信息禁止上传网络，仅限 .env / 环境变量读取
2. 项目 .soul/ 记忆数据仅在该项目上下文内可读
3. 全局身份 identity.md 仅写入 ~/.codex/soul/
4. 身份文件变更后需手动同步到各项目

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
