# 灵魂系统架构

## 设计模式

灵魂系统的架构受两个开源项目启发：

### 1. Microsoft MarkItDown —— 插件系统（核心架构模式）

| MarkItDown 模式 | 灵魂系统映射 |
|---|---|
| DocumentConverter 基类 | SoulBackend 基类 |
| DocumentConverterResult 结果类型 | SoulState / SoulEntry 数据类 |
| ConverterRegistration(converter, priority) | BackendRegistration(backend, priority) |
| PRIORITY_SPECIFIC_FILE_FORMAT (0.0) | PRIORITY_PRIMARY (0.0) |
| PRIORITY_GENERIC_FILE_FORMAT (10.0) | PRIORITY_SECONDARY (10.0) |
| entry_points(group="markitdown.plugin") | entry_points(group="soul.backend") |
| egister_converters(markitdown, **kwargs) | egister_backends(soul, **kwargs) |
| _load_plugins() 懒加载 | _load_plugins() 懒加载 |
| _convert() 排序+调度 | ead() 排序+调度 |
| __plugin_interface_version__ | __plugin_interface_version__ |
| __all__ 显式导出 | __all__ 显式导出 |


### 2. thedotmack/claude-mem —— 结构化记忆 + 双层存储

| claude-mem 模式 | 灵魂系统映射 | 版本 |
|---|---|---|
| memory_items (kind/type/facts/concepts/files) | SoulEntry (kind/facts/concepts/files) | v1.2 |
| SERVER_STORAGE_SCHEMA_VERSION (33) | SOUL_SCHEMA_VERSION (1) | v1.2 |
| FTS 全文检索 | Soul.search() | v1.2 |
| ContextBuilder + sections | Soul.compress() → CompressedContext | v1.2 |
| Hook 自动捕获 | scripts/soul-hook.ps1 | v1.2 |
| SQLite + Chroma 双层存储 | SqliteBackend (SQLite + FTS5) + FileBackend | **v1.3** |

### 3. Andrej Karpathy / multica-ai —— 行为准则

四项原则已从"外部规则"转化为灵魂内置的判断习惯，写入 identity.md。

## 灵魂生命周期

`
安装 (install.ps1)
  │
  ├─ 创建 ~/knowledge/soul/
  ├─ 写入默认模板
  └─ 注入 soul 函数到 PowerShell profile

每次会话
  │
  ├─ 醒来 (SKILL.md 加载)
  │   ├─ Soul.read() → SqliteBackend.accepts() → SqliteBackend.read() OR FileBackend.read()
  │   └─ 返回 SoulState{heartbeat, identity, moments, evolution}
  │
  ├─ 生活中
  │   ├─ soul -m → SqliteBackend.write(tags=["moment"])  # SQLite 优先
  │   ├─ soul -r → SqliteBackend.write(tags=["reflect"])
  │   └─ soul -save → SqliteBackend.write(tags=["heartbeat"]) + 同步 @current.md
  │
  └─ 离开
      └─ 自动保存心跳
`

## 后端调度流程 (v1.3)

`
Soul.read(path)
  │
  ├─ 按优先级排序后端列表（稳定排序）
  │
  ├─ 对每个后端:
  │   ├─ backend.accepts(path) → True?
  │   │   └─ backend.read(path) → SoulState
  │   │       └─ SoulState 非空? → 返回
  │   └─ False → 下一个
  │
  ├─ 优先级: SqliteBackend (0.0) → FileBackend (10.0)
  │   → SQLite 数据库存在则返回，否则回退文件系统
  │
  └─ 无后端接受 → 返回空 SoulState
`

## 版本化接口

- __plugin_interface_version__ = 2 —— 插件接口版本
- soul/__about__.py —— 系统版本 v1.3.0
- SOUL_SCHEMA_VERSION = 1 —— 数据 schema 版本
- SoulVersionMismatch —— 数据版本不匹配错误

## 插件发现

插件通过 Python importlib.metadata.entry_points 发现：

`	oml
# pyproject.toml
[project.entry-points."soul.backend"]
my-backend = "my_package"
`

插件模块必须导出 egister_backends(soul) 或 __plugin_interface_version__。

## 学习来源对照

| 来源 | 贡献 | 版本引入 |
|---|---|---|
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | 插件架构: entry_points + 优先级注册 + 懒加载 | v1.1 |
| [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | 结构化记忆、双层存储、schema 版本、FTS、Hook | v1.2 → v1.3 SQLite 实现 |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | 四项行为准则 | v1.0 |
