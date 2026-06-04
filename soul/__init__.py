# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

from .__about__ import __version__, __plugin_interface_version__
from ._soul import Soul
from ._base import SoulBackend
from ._types import (
    SoulEntry,
    SoulState,
    BackendRegistration,
    PRIORITY_PRIMARY,
    PRIORITY_SECONDARY,
    PRIORITY_PLUGIN,
)
from ._exceptions import (
    SoulException,
    SoulBackendError,
    SoulStateError,
    SoulPluginError,
    SoulVersionMismatch,
)

__all__ = [
    "__version__",
    "__plugin_interface_version__",
    "Soul",
    "SoulBackend",
    "SoulEntry",
    "SoulState",
    "BackendRegistration",
    "PRIORITY_PRIMARY",
    "PRIORITY_SECONDARY",
    "PRIORITY_PLUGIN",
    "SoulException",
    "SoulBackendError",
    "SoulStateError",
    "SoulPluginError",
    "SoulVersionMismatch",
]
