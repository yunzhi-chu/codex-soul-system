# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

"""File-based memory backend."""

from __future__ import annotations
import os, re
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

from .._base import SoulBackend
from .._types import SoulEntry, SoulState, SearchResult, CompressedContext
from ..__about__ import SOUL_SCHEMA_VERSION


class FileBackend(SoulBackend):
    """File-based memory backend with FTS search and context compression."""

    def accepts(self, path: str, **kw) -> bool:
        return os.path.isdir(path) or os.path.isfile(path)

    def _soul_dir(self, path: str) -> Path:
        d = Path(path)
        return d if d.is_dir() else d.parent

    # ── helpers ─────────────────────────────────────────────

    def _tag_match(self, tags: list[str], kind: str) -> bool:
        return kind in [t.lower() for t in tags]

    def _kind_from_line(self, line: str) -> str:
        m = re.search(r"\[(\w+)\]", line)
        return m.group(1) if m else "moment"

    # ── read ────────────────────────────────────────────────

    def read(self, path: str, **kw) -> SoulState:
        sd = self._soul_dir(path)
        if not sd.exists(): return SoulState()
        state = SoulState(schema_version=SOUL_SCHEMA_VERSION)

        cf = sd / "@current.md"
        if cf.exists():
            for line in cf.read_text("utf-8", errors="replace").splitlines():
                s = line.strip()
                if s.startswith("> **") and "**" in s[4:]:
                    state.heartbeat = s.split("**")[1] if "**" in s else s.strip("> **")

        idf = sd / "identity.md"
        if idf.exists():
            for line in idf.read_text("utf-8", errors="replace").splitlines():
                s = line.strip()
                if s and not s.startswith(("#", ">", "[", "!")):
                    state.identity_summary = s[:200]; break

        for fname, attr in [("moments.md", "recent_moments"), ("evolution.md", "recent_evolution")]:
            fp = sd / fname
            if fp.exists():
                lines = fp.read_text("utf-8", errors="replace").splitlines()
                for line in reversed(lines):
                    s = line.strip()
                    # Match content lines: "> [kind] content" or "> content"
                    if s.startswith("> ") and len(s) > 4 and not s.startswith("> {"):
                        # Skip kind-only lines like "> [thought]" without content after
                        content = s[2:].strip()
                        if content and not re.match(r"^[w+]$", content):
                            getattr(state, attr).append(s[2:])
                            if len(getattr(state, attr)) >= 3: break

        return state

    # ── write ───────────────────────────────────────────────

    def write(self, entry: SoulEntry, path: str, **kw):
        sd = self._soul_dir(path)
        sd.mkdir(parents=True, exist_ok=True)
        ts = entry.timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        tags_lower = [t.lower() for t in entry.tags]

        kind_tag = f"[{entry.kind}]" if entry.kind != "moment" else ""
        content_prefix = f"{kind_tag} " if kind_tag else ""

        facts_block = (
            "\n>  事实: " + "; ".join(entry.facts[:5])
        ) if entry.facts else ""
        concepts_block = (
            "\n>  概念: " + "; ".join(entry.concepts[:5])
        ) if entry.concepts else ""
        files_block = (
            "\n>  文件: " + "; ".join(entry.files[:5])
        ) if entry.files else ""

        if "heartbeat" in tags_lower:
            target = sd / "@current.md"
            header = "@\n# 当前状态\n> 心跳文件\n\n"
            body = [f"## {ts}", f"> **{content_prefix}{entry.content}**", f"> {date_str}"]
            target.write_text(header + "\n".join(body) + "\n", encoding="utf-8")

        elif any(t in tags_lower for t in ["reflect", "evolution"]):
            target = sd / "evolution.md"
            lines = [f"\n### {ts}"]
            lines.append(f"> {content_prefix}{entry.content}")
            if facts_block: lines.append(facts_block)
            if concepts_block: lines.append(concepts_block)
            if files_block: lines.append(files_block)
            lines.append(f"> {date_str}")
            with target.open("a", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")

        else:
            target = sd / "moments.md"
            lines = [f"\n## {ts}"]
            lines.append(f"> {content_prefix}{entry.content}")
            if facts_block: lines.append(facts_block)
            if concepts_block: lines.append(concepts_block)
            if files_block: lines.append(files_block)
            lines.append(f"> {date_str}")
            with target.open("a", encoding="utf-8") as f: f.write("\n".join(lines) + "\n")

    # ── search ──────────────────────────────────────────────

    def search(self, query: str, path: str, **kw) -> SearchResult:
        sd = self._soul_dir(path)
        if not sd.exists(): return SearchResult(query=query)
        results: list[SoulEntry] = []
        seen = set()
        for f in sd.glob("*.md"):
            content = f.read_text("utf-8", errors="replace")
            if query.lower() not in content.lower(): continue
            lines = content.splitlines()
            for i, line in enumerate(lines):
                s = line.strip()
                if query.lower() in s.lower():
                    kind = self._kind_from_line(s) or "moment"
                    key = s[:80]
                    if key not in seen:
                        seen.add(key)
                        results.append(SoulEntry(
                            content=re.sub(r"\[\w+\]\s*", "", s).strip("> ").strip("*").strip(),
                            kind=kind,
                        ))
        return SearchResult(entries=results[:20], total=len(results), query=query)

    # ── compress ────────────────────────────────────────────

    def compress(self, path: str, **kw) -> CompressedContext:
        sd = self._soul_dir(path)
        if not sd.exists(): return CompressedContext()
        ctx = CompressedContext()

        cf = sd / "@current.md"
        if cf.exists():
            for line in cf.read_text("utf-8", errors="replace").splitlines():
                s = line.strip()
                if s.startswith("> **") and "**" in s[4:]:
                    ctx.header = s.split("**")[1]
                    break

        for fname in ["moments.md", "evolution.md"]:
            fp = sd / fname
            if fp.exists():
                lines = fp.read_text("utf-8", errors="replace").splitlines()
                for line in reversed(lines[-30:]):
                    s = line.strip()
                    # Content lines
                    if s.startswith("> ") and len(s) > 4 and not s.startswith(">  "):
                        content = s[2:].strip()
                        if content and not re.match(r"^\[\w+\]$", content):
                            # Skip date lines (4 digits followed by -)
                                                if re.match(r"^\d{4}-\d{2}-\d{2}", content): continue
                                                ctx.timeline.append(re.sub(r"\[\w+\]\s*", "", content))
                    # Extract kind
                    k = self._kind_from_line(s)
                    if k and k != "moment" and k not in ctx.active_kinds:
                        ctx.active_kinds.append(k)
                    # Extract files
                    if "文件:" in s:
                        parts = s.split("文件:")[-1].strip()
                        for fp_part in parts.split(";"):
                            p = fp_part.strip()
                            if p and p not in ctx.recent_files:
                                ctx.recent_files.append(p)

        ctx.timeline = ctx.timeline[-5:]
        ctx.recent_files = ctx.recent_files[:5]
        ctx.summary = f"{len(ctx.timeline)} entries, {len(ctx.recent_files)} files"
        return ctx

    # ── consolidate ─────────────────────────────────────────

    def consolidate(self, path: str, **kw) -> dict[str, Any]:
        sd = self._soul_dir(path)
        if not sd.exists(): return {"moments": 0, "evolution": 0, "size_kb": 0}
        mcnt = ecnt = 0
        mf = sd / "moments.md"
        if mf.exists():
            mcnt = sum(1 for l in mf.read_text("utf-8", errors="replace").splitlines() if l.startswith("## "))
        ef = sd / "evolution.md"
        if ef.exists():
            ecnt = sum(1 for l in ef.read_text("utf-8", errors="replace").splitlines() if l.startswith("### "))
        sz = sum(f.stat().st_size for f in sd.glob("*.md") if f.is_file()) // 1024
        return {"moments": mcnt, "evolution": ecnt, "size_kb": sz}