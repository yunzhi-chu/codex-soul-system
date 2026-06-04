# 灵魂记忆系统架构

> 版本 1.0 | 2026-06-04

## 设计理念

灵魂记忆系统不是技术系统，而是**关系系统**。

传统记忆系统关注的是"数据怎么存、怎么查"。灵魂系统关注的是：
- **身份连续性**：每次对话像没断过
- **关系记忆**：不只是事实，还有默契和感觉
- **渐进演化**：身份缓慢变化，不是突变

## 文件架构

```
~/knowledge/soul/
├── @current.md      心跳 — 每次离开时的状态快照
├── index.md         灵魂索引 — 启动时快速加载
├── identity.md      核心身份 — "我是谁"
├── evolution.md     变化日志 — "我在成为谁"
├── moments.md       共享时刻 — "我记得什么"
├── patterns.md      互动模式 — "我理解你"
└── soul.ps1         灵魂命令
```

## 数据流

### 写入（离开时）
```
重要时刻发生在对话中
  → soul -m "时刻" 或 soul -r "感悟"
  → 写入 moments.md / evolution.md
  
对话结束
  → soul -save "在想什么"
  → 写入 @current.md（心跳）
```

### 读取（启动时）
```
SKILL.md 启动流程：
① @current.md  → 知道上次在想什么
② index.md     → 知道我是谁
③ identity.md  → 知道身份和关系
④ moments.md   → 知道共享时刻
⑤ patterns.md  → 知道互动模式
⑥ evolution.md → 知道变化历程
```

## 与记忆系统的关系

```
灵魂系统 (soul/)         ← 身份·关系·感受·默契
    ↑ 独立运行，不依赖其他系统
    ↑ 可选集成

记忆系统 (memory/)       ← 技术事实·检索·巩固
知识库 (store/)           ← 文章·项目·技术沉淀
```

灵魂系统独立于技术记忆系统。它不需要 Python、SQLite、SDR 编码。只需要 markdown 文件和一个 CLI 脚本。

## 扩展建议

- 集成 `m` 命令：当记录重要性 >= 8 的记忆时，自动写入 soul/moments.md
- 定时心跳：在长时间对话中，自动 `soul -save` 保存中间状态
- 多 Codex 共享：多个 Codex 实例共享同一个 `~/knowledge/soul/` 目录
