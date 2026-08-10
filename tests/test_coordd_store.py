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


import threading


def _reg(store, *agents):
    for a in agents:
        store.register(a, protocol_version=coordd.Store.PROTOCOL_VERSION)


def test_claim_requires_registered_compatible_agent_and_task(tmp_path):
    store = mkstore(tmp_path)
    store.create_task("t1", "demo")
    import pytest
    with pytest.raises(coordd.Denied):
        store.claim("ghost", "t1", ["docs/"])
    store.register("old", protocol_version=0)
    with pytest.raises(coordd.Denied):
        store.claim("old", "t1", ["docs/"])
    _reg(store, "a1")
    with pytest.raises(coordd.NotFound):
        store.claim("a1", "missing", ["docs/"])


def test_claim_sets_owner_state_generation(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    got = store.claim("a1", "t1", ["rust/src/bin/x.rs"])
    assert got["generation"] == 1
    task = store.tasks(state="claimed")[0]
    assert (task["id"], task["owner"]) == ("t1", "a1")


def test_second_claim_conflicts_and_overlap_blocks(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    _reg(store, "a1", "a2")
    store.create_task("t1", "demo")
    store.create_task("t2", "demo2")
    store.claim("a1", "t1", ["docs/reports/"])
    with pytest.raises(coordd.Conflict):
        store.claim("a2", "t1", ["docs/reports/"])          # same task
    with pytest.raises(coordd.Conflict):
        store.claim("a2", "t2", ["docs/"])                  # prefix overlap
    store.claim("a2", "t2", ["cgauto/"])                    # disjoint proceeds


def test_twenty_simultaneous_claims_one_owner(tmp_path):
    store = mkstore(tmp_path)
    agents = [f"a{i}" for i in range(20)]
    _reg(store, *agents)
    store.create_task("t1", "contested")
    wins, errs = [], []

    def worker(name):
        try:
            wins.append((name, store.claim(name, "t1", ["docs/x"])["generation"]))
        except coordd.Conflict:
            errs.append(name)

    threads = [threading.Thread(target=worker, args=(a,)) for a in agents]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(wins) == 1 and len(errs) == 19
