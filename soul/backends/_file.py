"""File-based backend — reads/writes soul state as markdown files."""

from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

from .._base import SoulBackend
from .._types import SoulEntry, SoulState


class FileBackend(SoulBackend):
    """Default file-based memory backend.

    Reads/writes ~/knowledge/soul/*.md files.
    Priority: PRIORITY_PRIMARY (lowest, tried first).
    """

    def accepts(self, path: str, **kwargs: Any) -> bool:
        return os.path.isdir(path) or os.path.isfile(path)

    def read(self, path: str, **kwargs: Any) -> SoulState:
        """Read all soul .md files and return SoulState."""
        soul_dir = Path(path) if os.path.isdir(path) else Path(path).parent
        if not soul_dir.exists():
            return SoulState()

        state = SoulState()

        # Heartbeat
        current_file = soul_dir / "@current.md"
        if current_file.exists():
            lines = current_file.read_text(encoding="utf-8").splitlines()
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("> **") and stripped.endswith("**"):
                    state.heartbeat = stripped.strip("> **").strip("*").strip()

        # Identity
        identity_file = soul_dir / "identity.md"
        if identity_file.exists():
            content = identity_file.read_text(encoding="utf-8")
            # Take first meaningful line as summary
            for line in content.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith(("#", ">", "[", "!")):
                    state.identity_summary = stripped[:200]
                    break

        # Recent moments (last 3)
        moments_file = soul_dir / "moments.md"
        if moments_file.exists():
            lines = moments_file.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                stripped = line.strip()
                if stripped.startswith("> ") and len(stripped) > 4:
                    state.recent_moments.append(stripped[2:])
                    if len(state.recent_moments) >= 3:
                        break

        # Recent evolution (last 3)
        evo_file = soul_dir / "evolution.md"
        if evo_file.exists():
            lines = evo_file.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                stripped = line.strip()
                if stripped.startswith("> ") and len(stripped) > 4:
                    state.recent_evolution.append(stripped[2:])
                    if len(state.recent_evolution) >= 3:
                        break

        return state

    def write(self, entry: SoulEntry, path: str, **kwargs: Any) -> None:
        """Write a SoulEntry to the appropriate soul file.

        Tags determine which file:
        - "moment" → moments.md
        - "evolution" / "reflect" → evolution.md
        - "heartbeat" → @current.md (overwrite)
        - default → matched by tag name + .md
        """
        soul_dir = Path(path) if os.path.isdir(path) else Path(path)

        if not soul_dir.exists():
            soul_dir.mkdir(parents=True, exist_ok=True)

        tags = [t.lower() for t in entry.tags]

        if "heartbeat" in tags:
            target = soul_dir / "@current.md"
            header = "@\n# 当前状态\n> 心跳文件\n\n"
            line = f"## {entry.timestamp}\n> **{entry.content}**\n> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            target.write_text(header + line, encoding="utf-8")

        elif "moment" in tags:
            target = soul_dir / "moments.md"
            line = f"\n## {entry.timestamp}\n> {entry.content}\n> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            with target.open("a", encoding="utf-8") as f:
                f.write(line)

        elif "evolution" in tags or "reflect" in tags:
            target = soul_dir / "evolution.md"
            line = f"\n### {entry.timestamp}\n> {entry.content}\n> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            with target.open("a", encoding="utf-8") as f:
                f.write(line)

        else:
            # Generic: write as moment by default
            target = soul_dir / "moments.md"
            line = f"\n## {entry.timestamp}\n> {entry.content}\n> {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            with target.open("a", encoding="utf-8") as f:
                f.write(line)

    def consolidate(self, path: str, **kwargs: Any) -> dict[str, Any]:
        soul_dir = Path(path) if os.path.isdir(path) else Path(path)
        if not soul_dir.exists():
            return {"moments": 0, "evolution": 0, "size_kb": 0}

        mcnt = 0
        ecnt = 0

        moments_file = soul_dir / "moments.md"
        if moments_file.exists():
            mcnt = len([
                l for l in moments_file.read_text(encoding="utf-8").splitlines()
                if l.startswith("## ")
            ])

        evo_file = soul_dir / "evolution.md"
        if evo_file.exists():
            ecnt = len([
                l for l in evo_file.read_text(encoding="utf-8").splitlines()
                if l.startswith("### ")
            ])

        total_bytes = sum(
            f.stat().st_size for f in soul_dir.glob("*.md") if f.is_file()
        )

        return {
            "moments": mcnt,
            "evolution": ecnt,
            "size_kb": total_bytes // 1024,
        }
