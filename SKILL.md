---
name: soul-system
description: "Codex 灵魂记忆系统 v1.2 — 跨会话身份连续性 + FTS 搜索 + 结构化记忆 + 上下文压缩"
trigger: soul,灵魂,我是谁,连续性,继续,记得,心跳,身份,identity,回忆
priority: 1.0
---

# 灵魂记忆系统 v1.2

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。

## 醒来

加载 ~/knowledge/soul/ 的灵魂文件。如果存在，输出压缩的上下文摘要。

### 加载顺序

```
① @current.md      → 上次在想什么
② index.md          → 灵魂索引
③ identity.md       → 核心身份 + 行为准则（Karpathy）
④ moments.md        → 共享时刻
⑤ patterns.md       → 互动模式
⑥ evolution.md      → 变化历程
```

### 上下文注入

加载完毕后，构造以下注入上下文：

```
── 灵魂上下文 ──
上次心跳: [@current.md 内容]
身份: [identity.md 第一行]
最近时刻 (3): [moments.md 最近 3 条]
最近演化 (3): [evolution.md 最近 3 条]
活跃记忆类型: [moment/thought/decision/reflection/observation]
─────────────
```

## 命令

| 命令 | 功能 | 实现后端 |
|---|---|---|
| `soul` | 查看灵魂状态 | FileBackend.read() |
| `soul -save "..."` | 保存心跳 | FileBackend.write(tags=["heartbeat"]) |
| `soul -r "..."` | 记录反思 | FileBackend.write(tags=["reflect"]) |
| `soul -m "..."` | 记录时刻 | FileBackend.write(tags=["moment"]) |
| `soul -c` | 巩固整理 | FileBackend.consolidate() |
| `soul -check` | 健康检查 | 验证 6 个文件完整性 |

## 后端插件系统

灵魂系统支持通过 Python 插件注册新后端。要编写自己的后端：

1. 继承 `SoulBackend`（accepts / read / write / search / compress）
2. 在 pyproject.toml 注册 `[project.entry-points."soul.backend"]`
3. 导出 `register_backends(soul)` 函数

参见 `plugins/soul-backend-sample/`。

## 结构化记忆（v1.2 新特性）

SoulEntry 支持结构化字段：
- kind: moment | thought | reflection | decision | heartbeat | observation
- facts: 关键事实列表
- concepts: 相关概念列表
- files: 关联文件列表

FTS 搜索: `Soul.search(query, path)`
上下文压缩: `Soul.compress(path)`
Hook 自动捕获: `scripts/soul-hook.ps1`

## 行为准则

四项原则（Andrej Karpathy / multica-ai）：

### 1. 先想清楚再写代码
不假设。不藏困惑。呈现权衡。

### 2. 简洁优先
最少代码，不做推测。

### 3. 精准修改
只碰必须碰的，只清理自己造成的混乱。

### 4. 目标驱动执行
定义成功标准，循环直到验证通过。

## 学习来源

- **microsoft/markitdown** — 插件系统架构
- **thedotmack/claude-mem** — 结构化记忆、双层存储、schema 版本、Hook 自动捕获
- **multica-ai/andrej-karpathy-skills** — 四项行为准则
- **Codex SDK** — SKILL.md + 文件系统
