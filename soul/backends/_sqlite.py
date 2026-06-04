# SPDX-FileCopyrightText: 2024-present Codex Soul System Contributors
# SPDX-License-Identifier: MIT

"""
SQLite 记忆后端 —— 灵感来自 thedotmack/claude-mem 的双层存储 + Schema 版本追踪。

灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。

学习来源:
- https://github.com/thedotmack/claude-mem —— 结构化记忆 + FTS + schema 版本
- https://github.com/microsoft/markitdown —— 插件架构: entry_points + 优先级注册
"""

from __future__ import annotations
import os, re, sqlite3, threading, atexit
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

from .._base import SoulBackend
from .._types import SoulEntry, SoulState, SearchResult, CompressedContext
from ..__about__ import SOUL_SCHEMA_VERSION


class SqliteBackend(SoulBackend):
    """
    SQLite 记忆后端，支持 FTS5 全文搜索和结构化字段。
    支持多线程并发（WAL + busy_timeout）。
    """

    DB_FILENAME = ".soul.db"

    def __init__(self):
        self._conns: dict[int, sqlite3.Connection] = {}
        self._lock = threading.Lock()

    def _get_db(self, path: str) -> sqlite3.Connection:
        tid = threading.get_ident()
        if tid not in self._conns:
            db_path = self._db_path(path)
            conn = sqlite3.connect(str(db_path), timeout=15)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=10000")
            with self._lock:
                self._init_schema(conn)
            self._conns[tid] = conn
        return self._conns[tid]

    def close(self):
        with self._lock:
            for tid, conn in list(self._conns.items()):
                try:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                except Exception:
                    pass
                try:
                    conn.close()
                except Exception:
                    pass
            self._conns.clear()

    def _db_path(self, path: str) -> Path:
        sd = self._soul_dir(path)
        return sd / self.DB_FILENAME

    def _soul_dir(self, path: str) -> Path:
        d = Path(path)
        return d if d.is_dir() else d.parent

    def _init_schema(self, conn: sqlite3.Connection):
        conn.execute("CREATE TABLE IF NOT EXISTS soul_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        cur = conn.execute("SELECT value FROM soul_meta WHERE key = 'schema_version'")
        if cur.fetchone() is None:
            conn.execute("INSERT OR IGNORE INTO soul_meta (key, value) VALUES ('schema_version', ?)", (str(SOUL_SCHEMA_VERSION),))

        conn.execute("""
            CREATE TABLE IF NOT EXISTS soul_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL DEFAULT 'moment',
                content TEXT NOT NULL,
                title TEXT,
                facts TEXT DEFAULT '',
                concepts TEXT DEFAULT '',
                files TEXT DEFAULT '',
                tags TEXT DEFAULT '',
                metadata TEXT DEFAULT '{}',
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS soul_entries_fts
                USING fts5(content, kind, title, facts, concepts, files,
                    content=soul_entries, content_rowid=id)
            """)
        except sqlite3.OperationalError:
            pass

        conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_timestamp ON soul_entries(timestamp DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_kind ON soul_entries(kind)")
        conn.commit()

    def accepts(self, path: str, **kw: Any) -> bool:
        try:
            sd = self._soul_dir(path)
            return sd.exists()
        except Exception:
            return False

    def read(self, path: str, **kw: Any) -> SoulState:
        db_path = self._db_path(path)
        if not db_path.exists():
            return SoulState()

        conn = self._get_db(path)
        state = SoulState(schema_version=SOUL_SCHEMA_VERSION)

        cur = conn.execute("SELECT content FROM soul_entries WHERE kind = 'heartbeat' ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            state.heartbeat = row["content"]

        cur = conn.execute("SELECT content FROM soul_entries WHERE kind = 'identity' ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            state.identity_summary = row["content"][:200]

        cur = conn.execute(
            "SELECT content FROM soul_entries WHERE kind IN ('moment','thought','reflection','observation') ORDER BY id DESC LIMIT 3"
        )
        state.recent_moments = [r["content"] for r in cur.fetchall()]

        cur = conn.execute(
            "SELECT content FROM soul_entries WHERE kind IN ('decision','reflection') ORDER BY id DESC LIMIT 3"
        )
        state.recent_evolution = [r["content"] for r in cur.fetchall()]

        return state

    def write(self, entry: SoulEntry, path: str, **kw: Any) -> None:
        sd = self._soul_dir(path)
        sd.mkdir(parents=True, exist_ok=True)
        conn = self._get_db(path)

        ts = entry.timestamp or datetime.now().strftime("%Y%m%d-%H%M%S")

        for attempt in range(3):
            try:
                conn.execute(
                    """INSERT INTO soul_entries (kind, content, title, facts, concepts, files, tags, metadata, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (entry.kind, entry.content, entry.title or "",
                     "; ".join(entry.facts[:10]), "; ".join(entry.concepts[:10]),
                     "; ".join(entry.files[:10]), ", ".join(entry.tags),
                     str(entry.metadata) if entry.metadata else "{}", ts),
                )
                conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "locked" in str(e) and attempt < 2:
                    import time; time.sleep(0.1)
                else:
                    raise

        if "heartbeat" in [t.lower() for t in entry.tags]:
            try:
                self._sync_heartbeat_to_file(sd, entry, ts)
            except Exception:
                pass

    def _sync_heartbeat_to_file(self, sd: Path, entry: SoulEntry, ts: str):
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        target = sd / "@current.md"
        content = f"@\n# 当前状态\n> 心跳文件\n\n## {ts}\n> **{entry.content}**\n> {date_str}\n"
        target.write_text(content, encoding="utf-8")

    def search(self, query: str, path: str, **kw: Any) -> SearchResult:
        db_path = self._db_path(path)
        if not db_path.exists():
            return SearchResult(query=query)

        conn = self._get_db(path)
        entries: list[SoulEntry] = []

        try:
            cur = conn.execute(
                "SELECT kind, content, title, facts, concepts, files, timestamp "
                "FROM soul_entries_fts WHERE soul_entries_fts MATCH ? ORDER BY rank LIMIT 20",
                (query,),
            )
        except (sqlite3.OperationalError, sqlite3.DatabaseError):
            cur = conn.execute(
                "SELECT kind, content, title, facts, concepts, files, timestamp "
                "FROM soul_entries WHERE content LIKE ? OR facts LIKE ? OR concepts LIKE ? ORDER BY id DESC LIMIT 20",
                (f"%{query}%", f"%{query}%", f"%{query}%"),
            )

        for row in cur.fetchall():
            entries.append(SoulEntry(
                content=row["content"],
                kind=row["kind"],
                title=row["title"] or None,
                facts=[f.strip() for f in row["facts"].split(";") if f.strip()] if row["facts"] else [],
                concepts=[c.strip() for c in row["concepts"].split(";") if c.strip()] if row["concepts"] else [],
                files=[f.strip() for f in row["files"].split(";") if f.strip()] if row["files"] else [],
            ))

        return SearchResult(entries=entries, total=len(entries), query=query)

    def compress(self, path: str, **kw: Any) -> CompressedContext:
        db_path = self._db_path(path)
        if not db_path.exists():
            return CompressedContext()

        conn = self._get_db(path)
        ctx = CompressedContext()

        cur = conn.execute("SELECT content FROM soul_entries WHERE kind = 'heartbeat' ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            ctx.header = row["content"]

        cur = conn.execute("SELECT kind, content FROM soul_entries ORDER BY id DESC LIMIT 30")
        rows = cur.fetchall()
        ctx.timeline = [r["content"] for r in reversed(rows[-5:])]
        kinds = {r["kind"] for r in rows if r["kind"] and r["kind"] != "moment"}
        ctx.active_kinds = list(kinds)[:5]
        ctx.summary = f"{len(rows)} entries total, {len(kinds)} kinds active"
        return ctx

    def consolidate(self, path: str, **kw: Any) -> dict[str, Any]:
        db_path = self._db_path(path)
        if not db_path.exists():
            return {"entries": 0, "kinds": 0, "size_kb": 0}

        conn = self._get_db(path)
        cur = conn.execute("SELECT COUNT(*) as cnt FROM soul_entries")
        total = cur.fetchone()["cnt"]
        cur = conn.execute("SELECT COUNT(DISTINCT kind) as cnt FROM soul_entries")
        kinds = cur.fetchone()["cnt"]

        try:
            conn.execute("INSERT INTO soul_entries_fts(soul_entries_fts) VALUES('rebuild')")
        except Exception:
            pass

        size_kb = max(1, db_path.stat().st_size // 1024) if db_path.exists() else 0
        return {"entries": total, "kinds": kinds, "size_kb": size_kb}
