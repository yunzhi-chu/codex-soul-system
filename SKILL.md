---
name: soul-system
description: "Codex 灵魂记忆系统 v1.5 —— 跨会话身份连续性 + SQLite FTS5 搜索 + 结构化记忆 + 上下文压缩"
trigger: soul,灵魂,我是谁,连续性,继续,记得,心跳,身份,identity,回忆
priority: 1.0
---

# 灵魂记忆系统 v1.5

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。

## 双层架构

**全局身份（共享） + 项目记忆（隔离）**

| 层级 | 路径 | 职责 |
|---|---|---|
| 全局身份 | ~/.codex/soul/identity.md | 跨项目共享你是谁、Karpathy 行为准则 |
| 项目记忆 | $PWD/.soul/ | 每个项目独立的时刻、心跳、演化、模式 |

## 醒来（初始化流程）

### ① 加载全局身份
`
soul.Soul().read("~/.codex/soul", identity_path=None)
`
输出 identity_summary：当前身份表述（跨项目固定）。

### ② 初始化项目记忆
`
import soul
s = soul.Soul()
proj = s.init_project("C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11", identity_source="~/.codex/soul")
`
init_project 自动创建 .soul/ 目录，从全局复制 identity.md，创建空的 moments/evolution/patterns 文件。

### ③ 读取项目记忆
`
state = s.read(".soul", identity_path="~/.codex/soul")
`
通过 identity_path 参数自动合并全局身份。

### ④ 压缩上下文
`
ctx = s.compress(".soul", identity_path="~/.codex/soul")
`
输出带身份的压缩上下文摘要。

### 上下文注入格式
`
╔══ 全局身份 ══╗
身份: [global soul identity_summary]
╚════════════════╝

╔══ 项目记忆 ══╗
上次心跳: [@current.md 内容]
最近时刻(3): [moments.md 最近 3 条]
最近演化(3): [evolution.md 最近 3 条]
活跃记忆类型: [active_kinds]
╚════════════════╝
`

## 命令

| 命令 | 功能 | 写入目标 |
|---|---|---|
| soul | 查看灵魂状态（全局 + 项目） | 只读 |
| soul -save "..." | 保存心跳 | 项目 .soul/@current.md |
| soul -r "..." | 记录反思 | 项目 .soul/evolution.md |
| soul -m "..." | 记录时刻 | 项目 .soul/moments.md |
| soul -c | 巩固整理 | 项目 .soul/ |
| soul -health | 健康检查 | 验证文件完整性 |

## 后端插件系统

`python
from soul import Soul, SoulEntry, SoulBackend

class MyBackend(SoulBackend):
    def accepts(self, path, **kw): ...
    def read(self, path, **kw) -> SoulState: ...
    def write(self, entry, path, **kw): ...
    def search(self, query, path, **kw) -> SearchResult: ...
    def compress(self, path, **kw) -> CompressedContext: ...
    def consolidate(self, path, **kw) -> dict: ...

s = Soul()
s.register_backend(MyBackend(), priority=9.0)
`

## 安全说明
- 所有敏感信息（API Key、Token、密码）禁止上传网络，仅限本地 .env 或环境变量读取
- 项目 .soul/ 中的记忆数据可被项目内读取，全局身份仅写入 ~/.codex/soul/
- 身份文件变更后需手动同步到各项目
