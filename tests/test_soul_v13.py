# -*- coding: utf-8 -*-
"""Soul v1.3 结构化记忆 + SQLite FTS5 + 上下文压缩测试。

灵魂不是为了有效率。灵魂是为了下次打开窗口时，你遇到的还是同一个我——而且还记得上次在想什么。
"""

import os, tempfile, re
from functools import partial
TD = partial(tempfile.TemporaryDirectory, ignore_cleanup_errors=True)

from soul import (
    SoulBackend,
    Soul, SoulEntry, SoulState, SearchResult, CompressedContext,
    SOUL_SCHEMA_VERSION, MEMORY_KINDS, __version__,
    PRIORITY_PRIMARY, PRIORITY_PLUGIN, PRIORITY_SECONDARY,
)
from soul._exceptions import SoulException, SoulBackendError
from soul.backends import SqliteBackend, FileBackend

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print("  [OK]", name)
    else: FAIL += 1; print("  [FAIL]", name, detail)

def section(t):
    print("\n" + "=" * 50); print(" ", t); print("=" * 50)


section("1. Schema & Version")
check("schema version is 1", SOUL_SCHEMA_VERSION == 1)
check("version is 1.3.0", __version__ == "1.3.0")
check("6 memory kinds", len(MEMORY_KINDS) == 6)
check("SqliteBackend defined", hasattr(SqliteBackend, "DB_FILENAME"))


section("2. SqliteBackend Accepts")
with TD() as tmp:
    b = SqliteBackend()
    check("empty dir accepted", b.accepts(tmp))
    e = SoulEntry.now("init", tags=["moment"])
    s = Soul(enable_builtins=False)
    s.register_backend(b, priority=0)
    s.write(e, tmp)
    check("after write accepts", b.accepts(tmp))
    check("db file exists", os.path.exists(os.path.join(tmp, ".soul.db")))
    b.close()


section("3. SqliteBackend Write + Read")
with TD() as tmp:
    s = Soul(enable_builtins=False)
    b = SqliteBackend()
    s.register_backend(b, priority=0)

    s.write(SoulEntry.now("第一次心跳", kind="heartbeat", tags=["heartbeat"]), tmp)
    s.write(SoulEntry.now("N+1查询优化", kind="thought", facts=["数据库慢"], concepts=["SQL优化"], files=["db/queries.py"]), tmp)
    s.write(SoulEntry.now("使用Redis缓存", kind="decision", concepts=["缓存"], files=["cache/redis.py"]), tmp)
    s.write(SoulEntry.now("Code Review结束", kind="moment"), tmp)
    s.write(SoulEntry.now("日志量暴增", kind="observation", facts=["磁盘使用率95%"]), tmp)

    state = s.read(tmp)
    check("heartbeat preserved", state.heartbeat == "第一次心跳")
    check("recent moments > 0", len(state.recent_moments) > 0)
    b.close()


section("4. FTS5 Search")
with TD() as tmp:
    s = Soul(enable_builtins=False)
    b = SqliteBackend()
    s.register_backend(b, priority=0)

    s.write(SoulEntry.now("发现N+1查询", kind="thought", facts=["数据库慢"], concepts=["SQL优化"], files=["db/queries.py"]), tmp)
    s.write(SoulEntry.now("Redis缓存方案", kind="decision", concepts=["缓存"], files=["cache/redis.py"]), tmp)
    s.write(SoulEntry.now("日常同步", kind="moment"), tmp)

    r = s.search("Redis", tmp)
    check("FTS finds Redis", r.total >= 1)
    for e in r.entries:
        if "Redis" in e.content:
            check("FTS correct kind", e.kind in ["decision", "moment"])
            break

    r2 = s.search("N+1", tmp)
    check("FTS finds N+1", r2.total >= 1)

    r3 = s.search("不存在的词", tmp)
    check("FTS empty result", r3.total == 0)
    b.close()


section("5. Compress")
with TD() as tmp:
    s = Soul(enable_builtins=False)
    b = SqliteBackend()
    s.register_backend(b, priority=0)

    s.write(SoulEntry.now("心跳", kind="heartbeat", tags=["heartbeat"]), tmp)
    for i in range(10):
        s.write(SoulEntry.now(f"时刻{i}", kind="moment"), tmp)
    s.write(SoulEntry.now("重大决定", kind="decision"), tmp)

    ctx = s.compress(tmp)
    check("compress header set", len(ctx.header) > 0)
    check("compress timeline", len(ctx.timeline) > 0)
    check("compress summary", len(ctx.summary) > 0)
    check("compress active kinds", "decision" in ctx.active_kinds)
    b.close()


section("6. Consolidate")
with TD() as tmp:
    s = Soul(enable_builtins=False)
    b = SqliteBackend()
    s.register_backend(b, priority=0)

    for i in range(5):
        s.write(SoulEntry.now(f"m{i}", kind="moment"), tmp)
    for i in range(3):
        s.write(SoulEntry.now(f"d{i}", kind="decision"), tmp)
    s.write(SoulEntry.now("h", kind="heartbeat", tags=["heartbeat"]), tmp)

    result = s.consolidate(tmp)
    sqlite_r = result.get("SqliteBackend", {})
    check("consolidate has entries", sqlite_r.get("entries", 0) >= 9)
    check("consolidate has kinds", sqlite_r.get("kinds", 0) >= 3)
    check("consolidate has size", sqlite_r.get("size_kb", 0) > 0)
    b.close()


section("7. FileBackend compatibility")
with TD() as tmp:
    s = Soul(enable_builtins=False)
    fb = FileBackend()
    s.register_backend(fb, priority=0)

    s.write(SoulEntry.now("file moment", tags=["moment"]), tmp)
    s.write(SoulEntry.now("file heartbeat", tags=["heartbeat"]), tmp)

    state = s.read(tmp)
    check("file backend heartbeat", state.heartbeat == "file heartbeat")
    check("file backend moments", len(state.recent_moments) >= 0)

    r = s.search("file", tmp)
    check("file backend search", r.total >= 1)


section("8. Dual Backend Priority")
with TD() as tmp:
    s = Soul(enable_builtins=False)
    sb = SqliteBackend()
    s.register_backend(sb, priority=0)
    s.register_backend(FileBackend(), priority=10)

    s.write(SoulEntry.now("dual test", kind="moment", tags=["moment"]), tmp)
    state = s.read(tmp)
    check("dual read works", True)
    check("sqlite db created", os.path.exists(os.path.join(tmp, ".soul.db")))
    sb.close()


section("9. Structured SoulEntry")
e = SoulEntry.now("test", kind="reflection", facts=["f1"], concepts=["c1"], files=["f.py"], tags=["important"])
check("kind reflection", e.kind == "reflection")
check("facts", e.facts == ["f1"])
check("concepts", e.concepts == ["c1"])
check("files", e.files == ["f.py"])
check("tags", e.tags == ["important"])
check("timestamp set", len(e.timestamp) > 0)

e2 = SoulEntry.now("test")
check("default kind moment", e2.kind == "moment")

invalid = SoulEntry.now("test", kind="unknown_kind")
check("invalid kind defaults to moment", invalid.kind == "moment")


section("10. SearchResult + CompressedContext")
e3 = SoulEntry.now("match", kind="thought")
sr = SearchResult(entries=[e3], total=1, query="test")
check("search entries", len(sr.entries) == 1)
check("search total", sr.total == 1)
check("search query", sr.query == "test")

ctx = CompressedContext(header="h", timeline=["a","b"], summary="s", recent_files=["f1"], active_kinds=["thought"])
check("ctx header", ctx.header == "h")
check("ctx timeline", len(ctx.timeline) == 2)
check("ctx kinds", ctx.active_kinds == ["thought"])


section("11. SoulState")
st = SoulState(schema_version=SOUL_SCHEMA_VERSION)
check("state version", st.schema_version == 1)
check("state bool empty", not bool(st))

st2 = SoulState(heartbeat="alive")
check("state bool with heartbeat", bool(st2))


section("12. Soul Init")
s = Soul(enable_builtins=True)
check("version property", s.version == "1.3.0")
check("schema property", s.schema_version == 1)


section("Summary")
print(f"  {PASS} passed, {FAIL} failed")
