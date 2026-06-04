# 灵魂记忆系统架构 v1.3

## 双层存储架构

### 背景
不同项目的工作记忆应隔离，但 Codex 的身份应跨项目保持一致。

### 设计
`
~/.codex/soul/identity.md ────── 全局身份（共享）
C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11/.soul/                    ── 项目记忆（隔离）
    ├── @current.md             上次心跳
    ├── index.md                项目索引
    ├── identity.md             项目副本（从全局复制）
    ├── moments.md              时刻记录
    ├── patterns.md             互动模式
    └── evolution.md            变化历程
`

### 读写策略
| 操作 | 路径 |
|---|---|
| 读取全局身份 | Soul.read("~/.codex/soul") |
| 读取项目记忆 | Soul.read(".soul", identity_path="~/.codex/soul") |
| 写入心跳 | Soul.write(entry, ".soul") → @current.md |
| 写入时刻 | Soul.write(entry, ".soul") → moments.md |
| 写入反思 | Soul.write(entry, ".soul") → evolution.md |

### 初始化流程
`python
import soul
s = soul.Soul()
s.init_project("C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11", identity_source="~/.codex/soul")
`
init_project 自动从全局复制 identity.md，创建空的项目记忆文件。

### 身份同步
全局身份变更后需手动同步到各项目：
`python
soul.Soul().init_project("project_a", identity_source="~/.codex/soul")
# 重复执行会跳过已存在文件，删除 .soul/identity.md 后重新 init 即可更新
`

## 后端插件系统

### Soul 类 API

| 方法 | 参数 | 说明 |
|---|---|---|
| init_project(path, identity_source) | path: 项目路径 | 初始化项目 .soul/ 目录 |
| ead(path, identity_path=None) | path, optional global identity | 读取项目记忆，可选合并全局身份 |
| write(entry, path) | SoulEntry + path | 写入记忆到项目 |
| search(query, path) | query string + path | 全文搜索 |
| compress(path, identity_path=None) | path, optional global identity | 压缩上下文摘要 |
| consolidate(path) | path | 整理统计数据 |

### 自定义后端
`python
from soul import SoulBackend, SoulState, SoulEntry

class MyBackend(SoulBackend):
    def accepts(self, path, **kw): ...
    def read(self, path, **kw) -> SoulState: ...
    def write(self, entry, path, **kw): ...
    def search(self, query, path, **kw) -> SearchResult: ...
    def compress(self, path, **kw) -> CompressedContext: ...
    def consolidate(self, path, **kw) -> dict: ...
`

## 安全边界
1. API Key、Token 等敏感信息禁止上传网络，仅限 .env / 环境变量
2. 项目 .soul/ 数据仅在该项目上下文内可读
3. 全局身份 identity.md 仅写入 ~/.codex/soul/ 而非项目目录
4. 如密钥泄露，删除 .env 并重新配置

## 版本
v1.3.0 — 双层存储架构（全局身份 + 项目记忆隔离）