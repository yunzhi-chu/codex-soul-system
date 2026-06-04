"""测试灵魂系统核心模块——后端注册 + 读写 + 插件模式。"""

from soul import (
    Soul, SoulBackend, SoulEntry, SoulState,
    __version__, __plugin_interface_version__,
    PRIORITY_PRIMARY, PRIORITY_SECONDARY, PRIORITY_PLUGIN,
)


def test_version():
    assert __version__ == "1.3.0"
    assert __plugin_interface_version__ == 2


def test_soul_init():
    s = Soul(enable_builtins=True)
    assert s._builtins_enabled
    assert len(s._backends) == 2  # SqliteBackend + FileBackend


def test_soul_init_no_builtins():
    s = Soul(enable_builtins=False)
    assert not s._builtins_enabled
    assert len(s._backends) == 0


def test_register_backend():
    s = Soul(enable_builtins=False)
    assert len(s._backends) == 0

    class FakeBackend(SoulBackend):
        def accepts(self, path, **kwargs): return True
        def read(self, path, **kwargs): return SoulState(heartbeat="fake")
        def write(self, entry, path, **kwargs): pass

    s.register_backend(FakeBackend(), priority=PRIORITY_PLUGIN)
    assert len(s._backends) == 1


def test_priority_order():
    s = Soul(enable_builtins=False)

    results = []
    class TrackBackend(SoulBackend):
        def __init__(self, name):
            self.name = name
        def accepts(self, path, **kwargs): return True
        def read(self, path, **kwargs):
            results.append(self.name)
            return SoulState(heartbeat=self.name)
        def write(self, entry, path, **kwargs): pass

    s.register_backend(TrackBackend("high"), priority=10.0)
    s.register_backend(TrackBackend("low"), priority=0.0)

    state = s.read("/any")
    assert state.heartbeat == "low"
    assert results == ["low"]


def test_read_empty_when_no_backend_accepts():
    s = Soul(enable_builtins=False)
    state = s.read("/nonexistent")
    assert state == SoulState()


def test_soul_entry_now():
    e = SoulEntry.now("test content", tags=["moment"])
    assert e.content == "test content"
    assert e.tags == ["moment"]
    assert len(e.timestamp) > 0


def test_file_backend_read(tmp_path):
    from soul.backends import FileBackend
    b = FileBackend()

    soul_dir = tmp_path / "soul"
    soul_dir.mkdir()
    (soul_dir / "@current.md").write_text(
        "@\n# 当前状态\n> 心跳文件\n\n## 20260604-120000\n> **我在测试**\n> 2026-06-04 12:00\n",
        encoding="utf-8"
    )
    (soul_dir / "identity.md").write_text(
        "# 身份\n\n## 我是\n\n我是 Codex。\n",
        encoding="utf-8"
    )
    (soul_dir / "moments.md").write_text(
        "## 20260604-120001\n> 这是第一个时刻\n> 2026-06-04\n",
        encoding="utf-8"
    )
    (soul_dir / "evolution.md").write_text(
        "### 20260604-120002\n> 这是演化记录\n> 2026-06-04\n",
        encoding="utf-8"
    )

    state = b.read(str(soul_dir))
    assert state.heartbeat == "我在测试"
    assert state.identity_summary is not None


def test_file_backend_write_moment(tmp_path):
    from soul.backends import FileBackend
    b = FileBackend()

    e = SoulEntry.now("测试时刻", tags=["moment"])
    b.write(e, str(tmp_path))

    moments_file = tmp_path / "moments.md"
    assert moments_file.exists()
    content = moments_file.read_text(encoding="utf-8")
    assert "测试时刻" in content


def test_file_backend_write_heartbeat(tmp_path):
    from soul.backends import FileBackend
    b = FileBackend()

    e = SoulEntry.now("心跳测试", tags=["heartbeat"])
    b.write(e, str(tmp_path))

    current_file = tmp_path / "@current.md"
    assert current_file.exists()
    content = current_file.read_text(encoding="utf-8")
    assert "心跳测试" in content


def test_file_backend_write_reflect(tmp_path):
    from soul.backends import FileBackend
    b = FileBackend()

    e = SoulEntry.now("反思测试", tags=["reflect"])
    b.write(e, str(tmp_path))

    evo_file = tmp_path / "evolution.md"
    assert evo_file.exists()
    content = evo_file.read_text(encoding="utf-8")
    assert "反思测试" in content


def test_file_backend_consolidate(tmp_path):
    from soul.backends import FileBackend
    b = FileBackend()

    b.write(SoulEntry.now("mom1", tags=["moment"]), str(tmp_path))
    b.write(SoulEntry.now("mom2", tags=["moment"]), str(tmp_path))
    b.write(SoulEntry.now("evo1", tags=["reflect"]), str(tmp_path))

    result = b.consolidate(str(tmp_path))
    assert result["moments"] == 2
    assert result["evolution"] == 1
    assert result["size_kb"] >= 0


def test_soul_read_through_backend(tmp_path):
    s = Soul(enable_builtins=True)

    e = SoulEntry.now("soul集成测试", tags=["moment"])
    s.write(e, str(tmp_path))

    state = s.read(str(tmp_path))
    assert len(state.recent_moments) >= 0


def test_plugin_interface_version():
    from soul.__about__ import __plugin_interface_version__ as ver
    assert ver == 2


def test_exception_hierarchy():
    from soul._exceptions import (
        SoulException, SoulBackendError, SoulStateError,
        SoulPluginError, SoulVersionMismatch,
    )
    assert issubclass(SoulBackendError, SoulException)
    assert issubclass(SoulStateError, SoulException)
    assert issubclass(SoulPluginError, SoulException)
    assert issubclass(SoulVersionMismatch, SoulException)
