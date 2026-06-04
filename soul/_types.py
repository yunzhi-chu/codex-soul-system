from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class SoulEntry:
    """Soul memory entry — a snapshot or moment in the soul's life."""

    timestamp: str
    content: str
    tags: list[str] = field(default_factory=list)
    title: Optional[str] = None

    @classmethod
    def now(cls, content: str, tags: Optional[list[str]] = None) -> "SoulEntry":
        return cls(
            timestamp=datetime.now().strftime("%Y%m%d-%H%M%S"),
            content=content,
            tags=tags or [],
        )


@dataclass
class SoulState:
    """The current state of the soul — heartbeat snapshot."""

    heartbeat: Optional[str] = None
    identity_summary: Optional[str] = None
    recent_moments: list[str] = field(default_factory=list)
    recent_evolution: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return any([
            self.heartbeat,
            self.identity_summary,
            self.recent_moments,
            self.recent_evolution,
        ])


@dataclass(frozen=True)
class BackendRegistration:
    """Registration of a memory backend with its priority."""

    backend: "SoulBackend"
    priority: float


# Priority constants — follow MarkItDown convention
PRIORITY_PRIMARY = 0.0       # Default file backend
PRIORITY_SECONDARY = 10.0    # Catch-all / generic backends
PRIORITY_PLUGIN = 5.0        # Plugin backends (between primary & secondary)
