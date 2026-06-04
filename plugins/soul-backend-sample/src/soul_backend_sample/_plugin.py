# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

"""Sample plugin: adds a JSON-based memory backend.

Pattern: mirrors MarkItDown's markitdown-sample-plugin exactly.
"""

from soul import Soul, SoulBackend, SoulEntry, SoulState
from soul._types import PRIORITY_PLUGIN

__plugin_interface_version__ = 1


def register_backends(soul: Soul, **kwargs):
    """Register the JSON backend. Called automatically by Soul.enable_plugins()."""
    soul.register_backend(JsonBackend(), priority=PRIORITY_PLUGIN)


class JsonBackend(SoulBackend):
    """A JSON-file memory backend for portable soul state."""

    def accepts(self, path: str, **kwargs) -> bool:
        import os
        import json
        target = os.path.join(path, "soul.json") if os.path.isdir(path) else path
        return target.endswith(".json")

    def read(self, path: str, **kwargs) -> SoulState:
        import os, json
        target = os.path.join(path, "soul.json") if os.path.isdir(path) else path
        if not os.path.isfile(target):
            return SoulState()

        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)

        return SoulState(
            heartbeat=data.get("heartbeat"),
            identity_summary=data.get("identity_summary"),
            recent_moments=data.get("recent_moments", []),
            recent_evolution=data.get("recent_evolution", []),
        )

    def write(self, entry: SoulEntry, path: str, **kwargs) -> None:
        import os, json
        target = os.path.join(path, "soul.json") if os.path.isdir(path) else path

        # Read existing
        data = {}
        if os.path.isfile(target):
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)

        tags_lower = [t.lower() for t in entry.tags]
        if "heartbeat" in tags_lower:
            data["heartbeat"] = entry.content
        elif "moment" in tags_lower:
            data.setdefault("recent_moments", []).insert(0, entry.content)
            data["recent_moments"] = data["recent_moments"][:10]
        elif "evolution" in tags_lower or "reflect" in tags_lower:
            data.setdefault("recent_evolution", []).insert(0, entry.content)
            data["recent_evolution"] = data["recent_evolution"][:10]

        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
