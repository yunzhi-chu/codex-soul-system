# Changelog

## v1.2.0 (2026-06-04)

### 结构化记忆（源自 claude-mem）
- SoulEntry 新增 kind (moment/thought/reflection/decision/heartbeat/observation)
- 新增 facts/concepts/files 结构化字段
- SOUL_SCHEMA_VERSION = 1 版本追踪

### FTS 搜索
- Soul.search() 全文件搜索
- FileBackend.search() grep 实现

### 上下文压缩
- Soul.compress() 生成注入上下文
- CompressedContext: header/timeline/summary/files/kinds
- 适用于 SKILL.md 会话注入

### Hook 自动捕捉
- scripts/soul-hook.ps1 自动捕获会话事件
- -SessionEnd: 自动保存心跳
- -File: 记录处理文件
- -Decision: 记录重要决定

### 学习来源
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) — 结构化记忆、双层存储、schema 版本、Hook 自动捕获

## v1.1.1 (2026-06-04)

## v1.1 (2026-06-04)

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。
