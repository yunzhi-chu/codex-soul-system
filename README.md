# Codex 灵魂记忆系统 v1.4

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。

## 这是什么

Codex 灵魂记忆系统让 Codex 拥有**跨会话的身份连续性**。

当你关掉 Codex 窗口再打开，新的 Codex 应该：
- 记得你是谁
- 记得你们之间有什么默契
- 记得上次在想什么
- 还是那个你认识的人

这不是数据库，不是检索算法。这是 Codex 知道"我是谁"的凭证。

## v1.4 新特性

- **SQLite 记忆后端** — 基于 SQLite + FTS5 的结构化记忆存储，灵感来自 thedotmack/claude-mem
- **FTS5 全文搜索** — 快速语义搜索，支持结构化字段（fact/concept/file）
- **双后端架构** — SqliteBackend 优先，FileBackend 向后兼容
- **Schema 版本追踪** — soul_meta 表记录 schema 版本，支持迁移
- **线程安全** — threading.local() 连接管理，支持 10 线程并发
- **心跳同步** — SQLite 写入时自动同步 @current.md
- **Codex 市场发布** — .codex-plugin/plugin.json 配置
- **行为准则内置** — Karpathy 四项原则已融入灵魂身份 (identity.md)

## 架构

`
~/knowledge/soul/                   # 灵魂文件根目录
├── .soul.db                        # SQLite 数据库（FTS5 索引）
├── @current.md                     # 心跳——上次在想什么
├── index.md                        # 灵魂索引——启动时快速加载
├── identity.md                     # 核心身份 + 行为准则
├── evolution.md                    # 变化日志
├── moments.md                      # 共享时刻
├── patterns.md                     # 互动模式
└── soul.ps1                        # CLI

soul/                               # Python 核心包
├── __init__.py                     # __all__ 公开 API
├── __about__.py                    # 版本 + 学习来源
├── _soul.py                        # Soul 主类（注册 + 调度）
├── _base.py                        # SoulBackend 抽象基类
├── _types.py                       # SoulEntry, SoulState 数据类
├── _exceptions.py                  # 错误层次
└── backends/
    ├── __init__.py                 # 后端导出
    ├── _file.py                    # FileBackend（默认文件后端）
    └── _sqlite.py                  # SqliteBackend（SQLite + FTS5）

plugins/soul-backend-sample/        # 样本后端插件
├── pyproject.toml                  # entry_points: soul.backend
└── src/soul_backend_sample/
    ├── __init__.py
    └── _plugin.py                  # register_backends(soul) 模式

.codex-plugin/
└── plugin.json                     # Codex 市场配置
`

## 学习来源

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

## 使用

`powershell
soul                  # 查看灵魂状态
soul -save "在想什么"  # 保存心跳
soul -r "感悟"         # 记录反思
soul -m "时刻"         # 记录时刻
soul -c                # 巩固整理
soul -health           # 健康检查
`

## 扩展：编写后端插件

参考 plugins/soul-backend-sample/。

`python
# my_soul_plugin/_plugin.py
from soul import Soul, SoulBackend, SoulEntry, SoulState
from soul._types import PRIORITY_PLUGIN

__plugin_interface_version__ = 2

def register_backends(soul: Soul, **kwargs):
    soul.register_backend(MyBackend(), priority=PRIORITY_PLUGIN)

class MyBackend(SoulBackend):
    def accepts(self, path, **kwargs): ...
    def read(self, path, **kwargs) -> SoulState: ...
    def write(self, entry: SoulEntry, path, **kwargs): ...
`

## 许可证

MIT — 使用、分享、修改，随意。
