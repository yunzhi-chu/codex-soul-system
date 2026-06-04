# Changelog

## v1.4.0 (2026-06-04)

### 双层存储架构
- 全局身份共享: ~/.codex/soul/identity.md 跨项目一致
- 项目记忆隔离: .soul/ 每个项目独立的记忆目录
- init_project(path, identity_source) 自动初始化项目 .soul/ 目录

### Bug 修复
- SqliteBackend 连接缓存键从 `tid` 改为 `(tid, path)`，修复同一线程多路径内存泄漏
- Soul.read()/compress() identity_path 循环 fallthrough 修复

### API 变更
- `read`(path, identity_path=None) — 读取项目记忆时可选合并全局身份
- compress(path, identity_path=None) — 压缩上下文时可选合并全局身份
- init_project(path, identity_source) — 初始化项目 .soul/ 目录

### 安全
- 新增安全说明：禁止 API Key / Token 上传网络
- 身份文件变更后需手动同步到各项目

### 学习来源
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — 结构化记忆、双层存储、schema 版本、Hook
- [microsoft/markitdown](https://github.com/microsoft/markitdown) — 插件架构、entry_points、优先级注册
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — Karpathy 四项行为准则

灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。


## v1.3.0 (2026-06-04)

### SQLite 记忆后端（学习来源: thedotmack/claude-mem + microsoft/markitdown）
- SqliteBackend — 基于 SQLite + FTS5 的全新记忆后端
- 双后端架构: SqliteBackend 优先级最高，FileBackend 向后兼容
- 结构化表 soul_entries: kind/content/facts/concepts/files/tags/metadata
- FTS5 全文索引 soul_entries_fts，回退到 LIKE 搜索
- Schema 版本追踪: soul_meta 表 + SOUL_SCHEMA_VERSION
- 线程安全: `threading`.local() 连接管理
- 心跳同步: SQLite 写入心跳时自动同步到 @current.md

### 架构升级
- 双内置后端: SqliteBackend (PRIORITY_PRIMARY) + FileBackend (PRIORITY_SECONDARY)
- 后端优先级自动调度: SQLite 优先，文件系统回退
- 全面的异常处理: SQLite OperationalError 优雅降级

### Codex 市场发布
- .codex-plugin/plugin.json 市场配置文件
- 技能触发器: soul/灵魂/我是谁/连续性/心跳/身份/identity/回忆
- 插件入口点: soul.backend group

### 测试
- test_soul.py: 15 单元测试，适配 v1.3.0 双后端
- test_soul_v13.py: 12 大项结构化测试（SQLite FTS5 + 压缩 + 双后端）
- test_extreme.py: 27 极端测试（10线程并发 + 10K写入 + Unicode + 内存）

### 学习来源
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — 结构化记忆、双层存储、schema 版本、FTS、Hook
- [microsoft/markitdown](https://github.com/microsoft/markitdown) — 插件架构、entry_points 发现、优先级注册
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — 四项行为准则

## v1.2.0 (2026-06-04)

### 结构化记忆（源自 claude-mem）
- SoulEntry 新增 kind (moment/thought/reflection/decision/heartbeat/observation)
- 新增 facts/concepts/files 结构化字段
- SOUL_SCHEMA_VERSION = 1 版本追踪

### FTS 搜索
- Soul.search() 全文文件搜索
- FileBackend.search() grep 实现

### 上下文压缩
- Soul.compress() 生成注入上下文
- CompressedContext: header/timeline/summary/files/kinds
- 适用于 SKILL.md 会话注入

### Hook 自动捕获
- scripts/soul-hook.ps1 自动捕获会话事件
- -SessionEnd: 自动保存心跳
- -File: 记录处理文件
- -Decision: 记录重要决定

### 学习来源
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — 结构化记忆、双层存储、schema 版本、Hook 自动捕获

## v1.1.1 (2026-06-04)

## v1.1 (2026-06-04)

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。


