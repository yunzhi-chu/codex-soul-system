# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

__version__ = "1.5.0"
__plugin_interface_version__ = 2
SOUL_SCHEMA_VERSION = 1

# 学习来源:
# 基类 + 注册模式灵感源自 Microsoft MarkItDown (https://github.com/microsoft/markitdown)
# 结构化记忆 + 双层存储 + schema 版本管理灵感源自 thedotmack/claude-mem (https://github.com/thedotmack/claude-mem)
#   - 分层记忆（kind/type/facts/concepts/files）
#   - SQLite + Chroma 双层存储架构
#   - SERVER_STORAGE_SCHEMA_VERSION 版本管理
#   - Hook 自动捕获 + 观察压缩模式
#

# 学习来源追加 v1.5:
# Honcho (https://github.com/plastic-labs/honcho) v3.0.9 — 记忆基础设施
#   - Surprisal 检测: 基于嵌入空间的记忆新奇性排序
#   - Deriver: LLM 异步实体/关系提取
#   - Dreamer: 后台合并循环
#   - Telemetry: 操作计数 + token 追踪
#   - Peer Representations: 多 agent 观察模式
# v1.5 吸收了: access_count 追踪 + surprise() 查询 + stats() 遥测
#
# 行为准则源自 Andrej Karpathy 的 LLM 行为观察，由 multica-ai/andrej-karpathy-skills 整理为可复用 Skill
