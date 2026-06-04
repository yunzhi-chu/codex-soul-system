# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

__version__ = "1.4.0"
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
# 行为准则源自 Andrej Karpathy 的 LLM 行为观察，由 multica-ai/andrej-karpathy-skills 整理为可复用 Skill