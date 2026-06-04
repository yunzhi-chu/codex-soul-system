from __future__ import annotations
from typing import Any, Optional
from ._types import SoulEntry, SoulState, SearchResult, CompressedContext


class SoulBackend:
    """Abstract base for memory backends."""

    def accepts(self, path: str, **kwargs: Any) -> bool:
        raise NotImplementedError(f"{type(self).__name__} must implement accepts()")

    def read(self, path: str, **kwargs: Any) -> SoulState:
        raise NotImplementedError(f"{type(self).__name__} must implement read()")

    def write(self, entry: SoulEntry, path: str, **kwargs: Any) -> None:
        raise NotImplementedError(f"{type(self).__name__} must implement write()")

    def search(self, query: str, path: str, **kwargs: Any) -> SearchResult:
        """Full-text search across memory entries. Optional."""
        return SearchResult(query=query)

    def compress(self, path: str, **kwargs: Any) -> CompressedContext:
        """Generate compressed context for session injection. Optional."""
        return CompressedContext()

    def consolidate(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return {"moments": 0, "evolution": 0, "size_kb": 0}