# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

__version__ = "1.1.0"
__plugin_interface_version__ = 1

# 学习来源:
# 基类 + 注册模式灵感源自 Microsoft MarkItDown (https://github.com/microsoft/markitdown):
# - entry_points 插件发现
# - 优先级注册模式 (ConverterRegistration)
# - 懒加载 (lazy plugin loading)
# - 清晰基类层次 (DocumentConverter → convert + accepts)
#
# 行为准则源自 Andrej Karpathy 的 LLM 行为观察，
# 由 multica-ai/andrej-karpathy-skills 整理为可复用 Skill:
# 1. 先想清楚再写代码
# 2. 简洁优先
# 3. 精准修改
# 4. 目标驱动执行
