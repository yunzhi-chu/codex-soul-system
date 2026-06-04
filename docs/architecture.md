# 灵魂系统架构

## 设计模式

灵魂系统的架构受两个开源项目启发：

### 1. Microsoft MarkItDown — 插件系统（核心架构模式）

| MarkItDown 模式 | 灵魂系统映射 |
|---|---|
| `DocumentConverter` 基类 | `SoulBackend` 基类 |
| `DocumentConverterResult` 结果类型 | `SoulState` / `SoulEntry` 数据类 |
| `ConverterRegistration(converter, priority)` | `BackendRegistration(backend, priority)` |
| `PRIORITY_SPECIFIC_FILE_FORMAT` (0.0) | `PRIORITY_PRIMARY` (0.0) |
| `PRIORITY_GENERIC_FILE_FORMAT` (10.0) | `PRIORITY_SECONDARY` (10.0) |
| `entry_points(group="markitdown.plugin")` | `entry_points(group="soul.backend")` |
| `register_converters(markitdown, **kwargs)` | `register_backends(soul, **kwargs)` |
| `_load_plugins()` 懒加载 | `_load_plugins()` 懒加载 |
| `_convert()` 排序+调度 | `read()` 排序+调度 |
| `__plugin_interface_version__` | `__plugin_interface_version__` |
| `__all__` 显式导出 | `__all__` 显式导出 |

### 2. Andrej Karpathy / multica-ai — 行为准则

四项原则已从"外部规则"转化为灵魂内置的判断习惯，写入 identity.md。

## 灵魂生命周期

```
安装 (install.ps1)
  │
  ├─ 创建 ~/knowledge/soul/
  ├─ 写入默认模板
  └─ 注入 soul 函数到 PowerShell profile

每次会话
  │
  ├─ 醒来 (SKILL.md 加载)
  │   ├─ Soul.read() → FileBackend.accepts() → FileBackend.read()
  │   └─ 返回 SoulState{heartbeat, identity, moments, evolution}
  │
  ├─ 生活中
  │   ├─ soul -m → FileBackend.write(tags=["moment"])
  │   ├─ soul -r → FileBackend.write(tags=["reflect"])
  │   └─ soul -save → FileBackend.write(tags=["heartbeat"])
  │
  └─ 离开
      └─ 自动保存心跳
```

## 后端调度流程

```
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
  └─ 无后端接受 → 返回空 SoulState
```

## 版本化接口

- `__plugin_interface_version__ = 1` — 插件接口版本
- `soul/__about__.py` — 系统版本
- `SoulVersionMismatch` — 数据版本不匹配错误

## 插件发现

插件通过 Python `importlib.metadata.entry_points` 发现：

```toml
# pyproject.toml
[project.entry-points."soul.backend"]
my-backend = "my_package"
```

插件模块必须导出 `register_backends(soul)` 或 `__plugin_interface_version__`。
