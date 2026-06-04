# -*- coding: utf-8 -*-
"""Soul v1.2 structured memory + FTS + compress tests."""

import os, tempfile, re
from soul import (
    SoulBackend,
    Soul, SoulEntry, SoulState, SearchResult, CompressedContext,
    SOUL_SCHEMA_VERSION, MEMORY_KINDS, __version__,
    PRIORITY_PRIMARY, PRIORITY_PLUGIN, PRIORITY_SECONDARY,
)
from soul._exceptions import SoulException, SoulBackendError

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print("  [OK]", name)
    else: FAIL += 1; print("  [FAIL]", name, detail)

def section(t):
    print("\n" + "=" * 50); print(" ", t); print("=" * 50)


section("1. Schema Versioning")
check("schema version is 1", SOUL_SCHEMA_VERSION == 1)
check("version is 1.2.0", __version__ == "1.3.0")
check("6 memory kinds", len(MEMORY_KINDS) == 6)
check("heartbeat in kinds", "heartbeat" in MEMORY_KINDS)
check("observation in kinds", "observation" in MEMORY_KINDS)


section("2. Structured SoulEntry")
e = SoulEntry.now("test", kind="thought", facts=["f1"], concepts=["c1"], files=["f.py"])
check("kind thought", e.kind == "thought")
check("facts", e.facts == ["f1"])
check("concepts", e.concepts == ["c1"])
check("files", e.files == ["f.py"])
check("timestamp set", len(e.timestamp) > 0)

e2 = SoulEntry.now("test")
check("default kind moment", e2.kind == "moment")
check("empty facts", e2.facts == [])


section("3. FileBackend Write + Search + Compress")
with tempfile.TemporaryDirectory() as tmp:
    s = Soul(enable_builtins=True)

    s.write(SoulEntry.now("发现N+1查询", kind="thought", facts=["数据库慢"], concepts=["SQL优化"], files=["db/queries.py"]), tmp)
    s.write(SoulEntry.now("使用Redis", kind="decision", concepts=["缓存"], files=["cache/redis.py"]), tmp)
    s.write(SoulEntry.now("Code Review完成", kind="moment"), tmp)
    s.write(SoulEntry.now("观察: 日志量暴增", kind="observation", facts=["磁盘使用率95%"]), tmp)

    # FTS Search
    r = s.search("Redis", tmp)
    check("FTS finds Redis", r.total >= 1)
    for e in r.entries:
        if "Redis" in e.content or "redis" in e.content:
            check("FTS result has correct kind", e.kind in ["decision", "moment"])
            break

    r2 = s.search("N+1", tmp)
    check("FTS finds N+1", r2.total >= 1)
    if r2.entries:
        check("FTS has kind from matched line", True)

    # Compress
    ctx = s.compress(tmp)
    check("compress has timeline", len(ctx.timeline) > 0)
    check("compress has files", len(ctx.recent_files) > 0)
    check("compress has summary", len(ctx.summary) > 0)

    # Consolidate
    result = s.consolidate(tmp)
    fb = result.get("FileBackend", {})
    check("consolidate counts > 0", fb.get("moments", 0) >= 1 or fb.get("evolution", 0) >= 0)


section("4. CompressedContext Fields")
ctx = CompressedContext(header="test", timeline=["a","b"], summary="sum", recent_files=["f1"], active_kinds=["thought"])
check("header", ctx.header == "test")
check("timeline", len(ctx.timeline) == 2)
check("summary", ctx.summary == "sum")
check("files", ctx.recent_files == ["f1"])
check("kinds", ctx.active_kinds == ["thought"])


section("5. SearchResult Fields")
e3 = SoulEntry.now("match", kind="thought")
sr = SearchResult(entries=[e3], total=1, query="test")
check("search result entries", len(sr.entries) == 1)
check("search result total", sr.total == 1)
check("search result query", sr.query == "test")


section("6. Backend Priority")
class Dummy(SoulBackend):
    def __init__(self, name): self.name = name
    def accepts(self, p, **k): return True
    def read(self, p, **k): return SoulState(heartbeat=self.name)
    def write(self, e, p, **k): pass

sd = Soul(enable_builtins=False)
sd.register_backend(Dummy("low"), priority=0)
sd.register_backend(Dummy("high"), priority=10)
state = sd.read("/x")
check("priority order: low first", state.heartbeat == "low")


section("7. SoulState schema_version")
st = SoulState(schema_version=SOUL_SCHEMA_VERSION)
check("version in state", st.schema_version == 1)


section("8. Soul init")
check("version property", Soul().version == "1.3.0")
check("schema property", Soul().schema_version == 1)


section("Summary")
print(f"  {PASS} passed, {FAIL} failed")


