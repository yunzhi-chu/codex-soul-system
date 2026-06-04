from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


MEMORY_KINDS = ["moment", "thought", "reflection", "decision", "heartbeat", "observation"]


@dataclass
class SoulEntry:
    """Structured soul memory entry — inspired by claude-mem memory_items."""

    content: str
    kind: str = "moment"          # moment | thought | reflection | decision | heartbeat | observation
    title: Optional[str] = None
    facts: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if self.kind not in MEMORY_KINDS:
            self.kind = "moment"

    @classmethod
    def now(cls, content: str, *, kind: str = "moment",
            tags: Optional[list[str]] = None,
            facts: Optional[list[str]] = None,
            concepts: Optional[list[str]] = None,
            files: Optional[list[str]] = None) -> "SoulEntry":
        return cls(
            content=content,
            kind=kind,
            tags=tags or [],
            facts=facts or [],
            concepts=concepts or [],
            files=files or [],
        )


@dataclass
class SoulState:
    """Current soul state — heartbeat snapshot."""

    heartbeat: Optional[str] = None
    identity_summary: Optional[str] = None
    recent_moments: list[str] = field(default_factory=list)
    recent_evolution: list[str] = field(default_factory=list)
    schema_version: int = 0

    def __bool__(self) -> bool:
        return any([self.heartbeat, self.identity_summary,
                    self.recent_moments, self.recent_evolution])


@dataclass
class SearchResult:
    """Search result from a memory backend."""

    entries: list[SoulEntry] = field(default_factory=list)
    total: int = 0
    query: str = ""


@dataclass
class CompressedContext:
    """Compressed context for session injection — inspired by claude-mem context sections."""

    header: str = ""
    timeline: list[str] = field(default_factory=list)
    summary: str = ""
    recent_files: list[str] = field(default_factory=list)
    active_kinds: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BackendRegistration:
    """Registration of a memory backend with its priority."""

    backend: "SoulBackend"
    priority: float


PRIORITY_PRIMARY = 0.0
PRIORITY_SECONDARY = 10.0
PRIORITY_PLUGIN = 5.0