import sys, os
sys.path.insert(0, os.path.abspath("."))
from soul import Soul

s = Soul(enable_builtins=True)
soul_dir = os.path.expanduser("~/knowledge/soul")

if not os.path.isdir(soul_dir):
    print("soul dir not found at", soul_dir)
    sys.exit(1)

print("=== FTS Search ===")
r = s.search("本地测试", soul_dir)
print(f"hits: {r.total}")
for e in r.entries:
    print(f"  [{e.kind}] {e.content[:60]}")

print()
print("=== Compress ===")
ctx = s.compress(soul_dir)
print(f"timeline: {len(ctx.timeline)}")
print(f"kinds: {ctx.active_kinds}")
print(f"files: {ctx.recent_files}")

print()
print("=== State ===")
state = s.read(soul_dir)
print(f"heartbeat: {state.heartbeat}")
print(f"schema_v: {state.schema_version}")
print(f"recent_moments: {len(state.recent_moments)}")
print(f"recent_evolution: {len(state.recent_evolution)}")

print()
print("ALL OK")