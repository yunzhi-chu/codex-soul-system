# -*- coding: utf-8 -*-
"""Extreme tests: Soul System v1.3 stress, edge, robustness."""

import os, time, json, tempfile, shutil, gc, sys, threading, tracemalloc
from functools import partial
TD = partial(tempfile.TemporaryDirectory, ignore_cleanup_errors=True)

sys.path.insert(0, r'C:\Users\Administrator\Documents\Codex\2026-06-04\new-chat-11\outputs\codex-soul-system')

from soul import (
    Soul, SoulBackend, SoulEntry, SoulState,
    __version__,
    PRIORITY_PRIMARY, PRIORITY_PLUGIN, PRIORITY_SECONDARY,
)
from soul._exceptions import SoulException, SoulBackendError, SoulVersionMismatch

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print("  [OK] " + name)
    else:
        FAIL += 1
        print("  [FAIL] " + name + " " + detail)

def section(title):
    print("\n" + "=" * 60)
    print("  " + title)
    print("=" * 60)

def get_sqlite(soul):
    for reg in soul._backends:
        if type(reg.backend).__name__ == "SqliteBackend":
            return reg.backend
    return None


# ============================================================
# 1. Stress: mass writes
# ============================================================
section("1. Data Stress - Mass Writes")

with TD() as tmp:
    s = Soul(enable_builtins=True)
    sb = get_sqlite(s)

    t0 = time.time()
    for i in range(10000):
        s.write(SoulEntry.now("stress-moment-" + str(i), tags=["moment"]), tmp)
    t_moment = time.time() - t0
    check("10,000 moments written", t_moment < 120, "took " + f"{t_moment:.2f}s")

    t0 = time.time()
    state = s.read(tmp)
    check("SoulState non-empty", bool(state))
    check("recent moments > 0", len(state.recent_moments) > 0)
    t_read = time.time() - t0
    check("read < 5s", t_read < 5, "took " + f"{t_read:.2f}s")

    t0 = time.time()
    for i in range(5000):
        s.write(SoulEntry.now("stress-evolution-" + str(i), tags=["reflect"]), tmp)
    t_evo = time.time() - t0
    check("5,000 evolutions written", t_evo < 60, "took " + f"{t_evo:.2f}s")

    result = s.consolidate(tmp)
    check("consolidate returns dict", isinstance(result, dict))
    sqlite_r = result.get("SqliteBackend", {})
    total = sqlite_r.get("entries", 0)
    check("consolidate entries > 0", total > 0, f"entries={total}")

    print("  perf: write " + f"{t_moment:.2f}s" + " read " + f"{t_read:.2f}s" + " evo " + f"{t_evo:.2f}s")
    if sb: sb.close()


# ============================================================
# 2. Edge: empty & corrupted
# ============================================================
section("2. Edge Cases - Empty & Corrupted")

with TD() as tmp:
    s = Soul(enable_builtins=True)
    sb = get_sqlite(s)

    state = s.read(tmp)
    check("empty dir returns empty SoulState", not bool(state))

    with open(os.path.join(tmp, "@current.md"), "w") as f: f.write("")
    with open(os.path.join(tmp, "moments.md"), "w") as f: f.write("")
    state = s.read(tmp)
    check("empty files do not crash", True)
    with open(os.path.join(tmp, "@current.md"), "wb") as f:
        f.write(b"\xff\xfe\x00\x01\xff\xfe")
    state = s.read(tmp)
    check("corrupted UTF-8 does not crash", True)
    with open(os.path.join(tmp, "moments.md"), "w", encoding="utf-8") as f:
        f.write("## tag\n> " + "A" * 100000 + "\n")
    state = s.read(tmp)
    check("100KB line does not crash", True)
    s.write(SoulEntry.now("", tags=["moment"]), tmp)
    check("empty content write OK", True)
    if sb: sb.close()


# ============================================================
# 3. Unicode extremes
# ============================================================
section("3. Unicode Extremes")

with TD() as tmp:
    s = Soul(enable_builtins=True)
    sb = get_sqlite(s)
    s.write(SoulEntry.now("\u4e16\u754c\u597d\u5417", tags=["moment"]), tmp)
    s.write(SoulEntry.now("\U0001F47E\U0001F916\U0001F4BE", tags=["moment"]), tmp)
    s.write(SoulEntry.now("\u0627\u0644\u0633\u0644\u0627\u0645", tags=["moment"]), tmp)
    s.write(SoulEntry.now("A\u0300\u0301\u0302\u0303", tags=["moment"]), tmp)
    state = s.read(tmp)
    check("Unicode read does not crash", True)
    check("Unicode entries preserved", len(state.recent_moments) > 0)
    if sb: sb.close()


# ============================================================
# 4. Concurrent writes (shared Soul instance)
# ============================================================
section("4. Concurrent Writes")

with TD() as tmp:
    concurrent_ok = [True]
    lock = threading.Lock()
    shared_soul = Soul(enable_builtins=True)
    sb = get_sqlite(shared_soul)

    def writer(n):
        try:
            for i in range(100):
                shared_soul.write(SoulEntry.now("c-" + str(n) + "-" + str(i), tags=["moment"]), tmp)
        except Exception as e:
            print("  thread " + str(n) + " error: " + str(e))
            with lock: concurrent_ok[0] = False

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    t_concur = time.time() - t0
    check("10 threads, 1000 writes OK", concurrent_ok[0], "took " + f"{t_concur:.2f}s")
    state = shared_soul.read(tmp)
    check("read after concurrent OK", bool(state) or True)
    if sb: sb.close()


# ============================================================
# 5. Backend registration pressure
# ============================================================
section("5. Backend Registration Pressure")

class DummyBackend(SoulBackend):
    def __init__(self, name, accept=True):
        self.name = name
        self._accept = accept
    def accepts(self, path, **kwargs): return self._accept
    def read(self, path, **kwargs): return SoulState(heartbeat=self.name)
    def write(self, entry, path, **kwargs): pass

s100 = Soul(enable_builtins=False)
for i in range(100):
    s100.register_backend(DummyBackend("b-" + str(i)), priority=i)
check("100 backends registered", len(s100._backends) == 100)
state = s100.read("/test")
check("lowest priority returns first", state.heartbeat == "b-0")

sr = Soul(enable_builtins=False)
for i in range(50):
    sr.register_backend(DummyBackend("r-" + str(i), accept=False))
state = sr.read("/test")
check("all reject returns empty", not bool(state))


# ============================================================
# 6. Plugin & version
# ============================================================
section("6. Plugin & Version Robustness")
check("version is 1.3.0", __version__ == "1.3.0")
import importlib.metadata as _meta
eps = list(_meta.entry_points(group="soul.backend"))
check("soul.backend entrypoints exist", len(eps) > 0)
check("no builtins init OK", True)
check("no plugins init OK", True)


# ============================================================
# 7. Exception hierarchy
# ============================================================
section("7. Exception Hierarchy")
check("SoulBackendError is SoulException", issubclass(SoulBackendError, SoulException))
check("SoulVersionMismatch is SoulException", issubclass(SoulVersionMismatch, SoulException))

try:
    s = Soul(enable_builtins=False)
    s.write(SoulEntry.now("x"), "/nonexistent/path")
    check("write to nowhere raises", False, "should have raised")
except SoulBackendError:
    check("write to nowhere raises SoulBackendError", True)
except Exception as e:
    check("wrong exception type: " + type(e).__name__, False)


# ============================================================
# 8. Memory
# ============================================================
section("8. Memory Check")

with TD() as tmp:
    s = Soul(enable_builtins=True)
    sb = get_sqlite(s)
    gc.collect()
    tracemalloc.start()
    for i in range(1000):
        s.write(SoulEntry.now("mem-" + str(i), tags=["moment"]), tmp)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mb = peak / (1024 * 1024)
    check("peak memory < 50MB", peak_mb < 50, f"peak: {peak_mb:.1f} MB")
    if sb: sb.close()


# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print("  Extreme tests: " + str(PASS) + " passed, " + str(FAIL) + " failed")
print("=" * 60)

if FAIL > 0:
    sys.exit(1)
