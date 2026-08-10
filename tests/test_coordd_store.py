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
