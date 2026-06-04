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
        from .backends import FileBackend
        self.register_backend(FileBackend(), priority=PRIORITY_PRIMARY)
        self._builtins_enabled = True

    def enable_plugins(self, **kw):
        if self._plugins_enabled: return
        for plugin in _load_plugins():
            try:
                if hasattr(plugin, "register_backends"):
                    plugin.register_backends(self, **kw)
            except Exception: warn(f"Soul plugin failed to register")
        self._plugins_enabled = True

    def _sorted(self):
        return sorted(self._backends, key=lambda r: r.priority)

    def read(self, path: str, **kw) -> SoulState:
        for reg in self._sorted():
            try:
                if reg.backend.accepts(path, **kw):
                    state = reg.backend.read(path, **kw)
                    if state: return state
            except Exception: pass
        return SoulState()

    def write(self, entry: SoulEntry, path: str, **kw):
        for reg in self._sorted():
            if reg.backend.accepts(path, **kw):
                reg.backend.write(entry, path, **kw)
                return
        raise SoulBackendError(f"No backend accepts {path}")

    def search(self, query: str, path: str, **kw) -> SearchResult:
        """FTS across all backends, return merged results."""
        results = SearchResult(query=query)
        for reg in self._sorted():
            try:
                if reg.backend.accepts(path, **kw):
                    r = reg.backend.search(query, path, **kw)
                    results.entries.extend(r.entries)
                    results.total += r.total
            except Exception: pass
        return results

    def compress(self, path: str, **kw) -> CompressedContext:
        """Generate compressed context for session injection."""
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
            except Exception: pass
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