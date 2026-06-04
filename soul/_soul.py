from __future__ import annotations
import os, traceback, importlib.metadata as _metadata
from typing import Any, Optional
from warnings import warn

from ._base import SoulBackend
from ._types import (
    SoulEntry, SoulState, SearchResult, CompressedContext,
    BackendRegistration,
    PRIORITY_PRIMARY, PRIORITY_SECONDARY, PRIORITY_PLUGIN,
)
from ._exceptions import SoulBackendError
from .__about__ import __version__, __plugin_interface_version__, SOUL_SCHEMA_VERSION

_plugins: Optional[list[Any]] = None

def _load_plugins() -> list[Any]:
    global _plugins
    if _plugins is not None: return _plugins
    _plugins = []
    for ep in _metadata.entry_points(group="soul.backend"):
        try: _plugins.append(ep.load())
        except Exception: warn(f"Soul plugin {ep.name!r} failed to load")
    return _plugins


class Soul:
    def __init__(self, *, enable_builtins=None, enable_plugins=None, **kw):
        self._backends: list[BackendRegistration] = []
        self._builtins_enabled = False
        self._plugins_enabled = False
        if enable_builtins is None or enable_builtins:
            self.enable_builtins(**kw)
        if enable_plugins: self.enable_plugins(**kw)

    def register_backend(self, backend: SoulBackend, priority: float = PRIORITY_PLUGIN):
        self._backends.insert(0, BackendRegistration(backend=backend, priority=priority))

    def enable_builtins(self, **kw):
        if self._builtins_enabled: return
        from .backends import FileBackend, SqliteBackend
        self.register_backend(SqliteBackend(), priority=PRIORITY_PRIMARY)
        self.register_backend(FileBackend(), priority=PRIORITY_SECONDARY)
        self._builtins_enabled = True

    def enable_plugins(self, **kw):
        if self._plugins_enabled: return
        for plugin in _load_plugins():
            try:
                if hasattr(plugin, "register_backends"):
                    plugin.register_backends(self, **kw)
            except Exception: warn(f"Soul plugin failed to register")
        self._plugins_enabled = True

    def init_project(self, path: str, identity_source: str | None = None):
        """Initialize a project .soul/ directory with templates from identity_source."""
        from pathlib import Path as _Path
        proj_dir = _Path(path) / ".soul"
        proj_dir.mkdir(parents=True, exist_ok=True)

        if identity_source:
            id_src = _Path(identity_source) / "identity.md"
            id_dst = proj_dir / "identity.md"
            if id_src.exists() and not id_dst.exists():
                id_dst.write_text(id_src.read_text("utf-8", errors="replace"), encoding="utf-8")

        for fname in ("@current.md", "index.md", "moments.md", "patterns.md", "evolution.md"):
            fp = proj_dir / fname
            if not fp.exists():
                fp.write_text(f"# {fname}\n> (empty)\n", encoding="utf-8")

        return proj_dir

    def _sorted(self):
        return sorted(self._backends, key=lambda r: r.priority)

    def read(self, path: str, **kw) -> SoulState:
        """Read soul state from path, with optional identity_path merge."""
        identity_path = kw.pop("identity_path", None)
        state = SoulState()
        for reg in self._sorted():
            try:
                if reg.backend.accepts(path, **kw):
                    state = reg.backend.read(path, **kw)
                    if state: break
            except Exception:
                pass
        if identity_path and identity_path != path and not state.identity_summary:
            for reg in self._sorted():
                try:
                    if reg.backend.accepts(identity_path, **kw):
                        id_state = reg.backend.read(identity_path, **kw)
                        if id_state and id_state.identity_summary:
                            state.identity_summary = id_state.identity_summary
                            break
                except Exception:
                    pass
        return state

    def write(self, entry: SoulEntry, path: str, **kw):
        for reg in self._sorted():
            if reg.backend.accepts(path, **kw):
                reg.backend.write(entry, path, **kw)
                return
        raise SoulBackendError(f"No backend accepts {path}")

    def search(self, query: str, path: str, **kw) -> SearchResult:
        results = SearchResult(query=query)
        for reg in self._sorted():
            try:
                if reg.backend.accepts(path, **kw):
                    r = reg.backend.search(query, path, **kw)
                    results.entries.extend(r.entries)
                    results.total += r.total
            except Exception:
                pass
        return results

    def compress(self, path: str, **kw) -> CompressedContext:
        """Generate compressed context with identity_path merge support."""
        identity_path = kw.pop("identity_path", None)
        ctx = CompressedContext()
        for reg in self._sorted():
            try:
                if reg.backend.accepts(path, **kw):
                    c = reg.backend.compress(path, **kw)
                    if c.header: ctx.header = c.header or ctx.header
                    ctx.timeline.extend(c.timeline)
                    ctx.summary = c.summary or ctx.summary
                    ctx.recent_files.extend(c.recent_files)
                    ctx.active_kinds.extend(c.active_kinds)
            except Exception:
                pass
        if identity_path and identity_path != path and not ctx.header:
            for reg in self._sorted():
                try:
                    if reg.backend.accepts(identity_path, **kw):
                        id_ctx = reg.backend.compress(identity_path, **kw)
                        if id_ctx.header:
                            ctx.header = id_ctx.header
                            break
                except Exception:
                    pass
        return ctx

    def consolidate(self, path: str, **kw) -> dict[str, Any]:
        results = {}
        for reg in self._sorted():
            if reg.backend.accepts(path, **kw):
                results[type(reg.backend).__name__] = reg.backend.consolidate(path, **kw)
        return results or {"moments": 0, "evolution": 0, "size_kb": 0}

    @property
    def version(self) -> str:
        return __version__

    @property
    def schema_version(self) -> int:
        return SOUL_SCHEMA_VERSION