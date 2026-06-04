# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

from ._plugin import __plugin_interface_version__, register_backends, JsonBackend

__all__ = [
    "__plugin_interface_version__",
    "register_backends",
    "JsonBackend",
]
