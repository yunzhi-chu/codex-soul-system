"""Main Soul class — the central coordinator, modeled after MarkItDown."""

from __future__ import annotations
import os
import traceback
import importlib.metadata as _metadata
from typing import Any, Optional
from warnings import warn
from pathlib import Path

from ._base import SoulBackend
from ._types import (
    SoulEntry, SoulState, BackendRegistration,
    PRIORITY_PRIMARY, PRIORITY_SECONDARY, PRIORITY_PLUGIN,
)
from ._exceptions import (
    SoulException, SoulBackendError, SoulStateError, SoulPluginError,
)
from .__about__ import __version__, __plugin_interface_version__

# Lazy-loaded plugin list — same pattern as MarkItDown._plugins
_plugins: Optional[list[Any]] = None


def _load_plugins() -> list[Any]:
    """Lazy-load soul system plugins via entry_points."""
    global _plugins
    if _plugins is not None:
        return _plugins

    _plugins = []
    for entry_point in _metadata.entry_points(group="soul.backend"):
        try:
            _plugins.append(entry_point.load())
        except Exception:
            tb = traceback.format_exc()
            warn(f"Soul plugin '{entry_point.name}' failed to load, skipping:\n{tb}")

    return _plugins


class Soul:
    """Codex Soul — cross-session identity continuity.

    The Soul manages memory backends in a priority-ordered registration.
    When reading/writing, it tries backends in priority order.
    """

    def __init__(
        self,
        *,
        enable_builtins: Optional[bool] = None,
        enable_plugins: Optional[bool] = None,
        **kwargs: Any,
    ):
        self._backends: list[BackendRegistration] = []
        self._builtins_enabled = False
        self._plugins_enabled = False

        if enable_builtins is None or enable_builtins:
            self.enable_builtins(**kwargs)

        if enable_plugins:
            self.enable_plugins(**kwargs)

    # ── registration ──────────────────────────────────────────────

    def register_backend(
        self,
        backend: SoulBackend,
        priority: float = PRIORITY_PLUGIN,
    ) -> None:
        """Register a memory backend with a priority.

        Lower priority = tried first. Stable sort preserves registration order.
        Pattern: MarkItDown.register_converter().
        """
        self._backends.insert(
            0, BackendRegistration(backend=backend, priority=priority)
        )

    def enable_builtins(self, **kwargs: Any) -> None:
        """Register built-in backends (file-based)."""
        if self._builtins_enabled:
            return

        from .backends import FileBackend
        self.register_backend(FileBackend(), priority=PRIORITY_PRIMARY)

        self._builtins_enabled = True

    def enable_plugins(self, **kwargs: Any) -> None:
        """Load and register plugin-provided backends."""
        if self._plugins_enabled:
            return

        plugins = _load_plugins()
        for plugin in plugins:
            try:
                if hasattr(plugin, "register_backends"):
                    plugin.register_backends(self, **kwargs)
            except Exception:
                tb = traceback.format_exc()
                warn(f"Soul plugin failed to register:\n{tb}")

        self._plugins_enabled = True

    # ── core operations ───────────────────────────────────────────

    def read(self, path: str, **kwargs: Any) -> SoulState:
        """Read soul state by trying backends in priority order.

        Returns the first non-empty result.
        Pattern: MarkItDown._convert() with priority-sorted registrations.
        """
        sorted_registrations = sorted(
            self._backends, key=lambda r: r.priority
        )

        for registration in sorted_registrations:
            backend = registration.backend
            try:
                if not backend.accepts(path, **kwargs):
                    continue
                state = backend.read(path, **kwargs)
                if state:
                    return state
            except Exception as e:
                warn(f"{type(backend).__name__}.read() failed: {e}")

        return SoulState()

    def write(self, entry: SoulEntry, path: str, **kwargs: Any) -> None:
        """Write a soul entry using the first accepting backend."""
        sorted_registrations = sorted(
            self._backends, key=lambda r: r.priority
        )

        for registration in sorted_registrations:
            backend = registration.backend
            try:
                if backend.accepts(path, **kwargs):
                    backend.write(entry, path, **kwargs)
                    return
            except Exception as e:
                raise SoulBackendError(
                    f"{type(backend).__name__}.write() failed: {e}"
                ) from e

        raise SoulBackendError(f"No backend accepts path: {path}")

    def consolidate(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """Run consolidation on all accepting backends."""
        results = {}
        sorted_registrations = sorted(
            self._backends, key=lambda r: r.priority
        )

        for registration in sorted_registrations:
            backend = registration.backend
            try:
                if backend.accepts(path, **kwargs):
                    results[type(backend).__name__] = backend.consolidate(path, **kwargs)
            except Exception as e:
                warn(f"{type(backend).__name__}.consolidate() failed: {e}")

        if not results:
            return {"moments": 0, "evolution": 0, "size_kb": 0}
        return results

    @property
    def version(self) -> str:
        return __version__
