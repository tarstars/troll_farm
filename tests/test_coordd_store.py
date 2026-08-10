"""Store-level semantics for coordd — the eight guarantees of spec §3, each testable."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import coordd


def mkstore(tmp_path, **kw):
    return coordd.Store(db_path=str(tmp_path / "c.sqlite3"), **kw)


def test_init_creates_schema_in_wal_mode(tmp_path):
    store = mkstore(tmp_path)
    con = sqlite3.connect(store.db_path)
    tables = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"agents", "tasks", "task_paths", "leases", "events", "acks",
            "artifacts", "reviews", "meta"} <= tables
    assert con.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    con.close()


def test_register_compatible_and_incompatible(tmp_path):
    store = mkstore(tmp_path)
    ok = store.register("claude_1", role="contributor", tool_digest="abc",
                        protocol_version=coordd.Store.PROTOCOL_VERSION)
    assert ok == {"agent": "claude_1", "compatible": True}
    old = store.register("chatgpt_1", protocol_version=0)
    assert old["compatible"] is False


def test_register_is_upsert(tmp_path):
    store = mkstore(tmp_path)
    store.register("claude_1", protocol_version=0)
    assert store.register("claude_1", protocol_version=1)["compatible"] is True
