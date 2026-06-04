"""Soul backend base class — inspired by MarkItDown's DocumentConverter interface."""

from __future__ import annotations
from typing import Any
from ._types import SoulEntry, SoulState


class SoulBackend:
    """Abstract base class for all memory backends.

    Subclasses must implement read() and write().
    The accepts() method allows the registration system to select the right backend.
    
    Pattern: MarkItDown's DocumentConverter.accepts() + convert().
    """

    def accepts(self, path: str, **kwargs: Any) -> bool:
        """Return True if this backend can handle the given soul path."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement accepts()"
        )

    def read(self, path: str, **kwargs: Any) -> SoulState:
        """Read the soul state from the given path.

        Returns an empty SoulState if nothing is found.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement read()"
        )

    def write(self, entry: SoulEntry, path: str, **kwargs: Any) -> None:
        """Write a soul entry to the given path."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement write()"
        )

    def consolidate(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """Optional: consolidate/analyze soul data at path.

        Returns a summary dict. Default returns empty.
        """
        return {"moments": 0, "evolution": 0, "size_kb": 0}
