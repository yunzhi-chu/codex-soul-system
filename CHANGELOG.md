# Changelog

## v1.1 (2026-06-04)

### 新架构
- 插件式后端架构 — 基于 Microsoft MarkItDown 模式
  - SoulBackend 抽象基类（accepts / read / write / consolidate）
  - BackendRegistration 优先级注册（PRIORITY_PRIMARY / PRIORITY_PLUGIN / PRIORITY_SECONDARY）
  - entry_points(group="soul.backend") 插件发现
  - 懒加载：插件在首次使用时加载
- 样本后端插件 (plugins/soul-backend-sample/) — JSON 后端完整实现
- 错误层次 (SoulException -> SoulBackendError 等)

### 行为准则
- Karpathy 四原则从 SKILL.md 融入 identity.md 作为灵魂内置身份
- SKILL.md 行为准则部分保留为 Codex 集成参考

### CLI
- soul -check 健康检查（验证所有 6 个文件 + 行为准则完整性）
- 健壮的错误处理（try/catch 文件操作）
- 更好的输出格式化（最近时刻 + 最近演化分开展示）

### 学习来源
- [microsoft/markitdown](https://github.com/microsoft/markitdown) — 插件系统架构
- [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — 行为准则

### 内部
- Python 包：soul/ 模块化，__all__ 显式导出
- 15 个测试用例覆盖核心逻辑
- 版本号统一为 1.1.0

> 灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。
