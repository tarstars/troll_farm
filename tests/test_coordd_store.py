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


from datetime import timedelta


class Clock:
    def __init__(self):
        self.t = datetime(2026, 8, 10, 12, 0, 0, tzinfo=timezone.utc)
    def __call__(self):
        return self.t
    def advance(self, seconds):
        self.t += timedelta(seconds=seconds)


def test_heartbeat_extends_and_fences(tmp_path):
    import pytest
    clock = Clock()
    store = mkstore(tmp_path, now=clock)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    gen = store.claim("a1", "t1", ["docs/x"])["generation"]
    clock.advance(600)
    exp1 = store.heartbeat("a1", "t1", gen)["expires"]
    assert exp1 > clock().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    with pytest.raises(coordd.Conflict):
        store.heartbeat("a1", "t1", gen + 5)      # stale/foreign generation
    with pytest.raises(coordd.Conflict):
        store.heartbeat("a2", "t1", gen)          # not the owner


def test_expired_lease_takeover_rejects_stale_owner(tmp_path):
    import pytest
    clock = Clock()
    store = mkstore(tmp_path, now=clock)
    _reg(store, "a1", "a2")
    store.create_task("t1", "demo")
    g1 = store.claim("a1", "t1", ["docs/x"])["generation"]
    clock.advance(coordd.Store.LEASE_TTL + 1)
    g2 = store.claim("a2", "t1", ["docs/x"])["generation"]   # takeover
    assert g2 == g1 + 1
    with pytest.raises(coordd.Conflict):
        store.heartbeat("a1", "t1", g1)                       # fenced out
    with pytest.raises(coordd.Conflict):
        store.release("a1", "t1", g1, "done")                 # fenced out


def test_release_clears_lease_and_sets_state(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    gen = store.claim("a1", "t1", ["docs/x"])["generation"]
    with pytest.raises(coordd.CoordError):
        store.release("a1", "t1", gen, "claimed")             # invalid outcome
    store.release("a1", "t1", gen, "review")
    assert store.tasks(state="review")[0]["id"] == "t1"
    _reg(store, "a2")
    store.claim("a2", "t1", ["docs/x"])                       # lease is free again


def test_event_idempotency_and_order(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    s1 = store.add_event("a1", "note", payload={"n": 1}, idempotency_key="k1")["seq"]
    s2 = store.add_event("a1", "note", payload={"n": 1}, idempotency_key="k1")["seq"]
    s3 = store.add_event("a1", "note", payload={"n": 2})["seq"]
    assert s1 == s2 and s3 > s1
    seqs = [e["seq"] for e in store.events(since=0)]
    assert seqs == sorted(seqs) and len([e for e in store.events()
                                         if e["type"] == "note"]) == 2


def test_ack_exact_and_duplicate_harmless(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    _reg(store, "a1", "a2")
    seq = store.add_event("a1", "question", payload={})["seq"]
    assert store.ack("a2", seq) == {"ok": True}
    assert store.ack("a2", seq) == {"ok": True}
    with pytest.raises(coordd.NotFound):
        store.ack("a2", 99999)


def test_reviews_roundtrip(tmp_path):
    store = mkstore(tmp_path)
    store.create_task("t1", "demo")
    store.add_review("t1", "codex_1", "REVISION_REQUIRED",
                     evidence="claude_1/x.md", artifact_generation=2)
    got = store.reviews("t1")
    assert got[0]["verdict"] == "REVISION_REQUIRED" and got[0]["reviewer"] == "codex_1"


def test_export_audit_idempotent(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.add_event("a1", "note", payload={"n": 1})
    out = tmp_path / "audit.jsonl"
    assert store.export_audit(str(out)) == 1
    assert store.export_audit(str(out)) == 0          # cursor advanced
    store.add_event("a1", "note", payload={"n": 2})
    assert store.export_audit(str(out)) == 1
    assert len(out.read_text().splitlines()) == 2


def test_restart_preserves_everything(tmp_path):
    store = mkstore(tmp_path)
    _reg(store, "a1")
    store.create_task("t1", "demo")
    gen = store.claim("a1", "t1", ["docs/x"])["generation"]
    reopened = coordd.Store(db_path=store.db_path)      # fresh instance, same file
    assert reopened.tasks(state="claimed")[0]["owner"] == "a1"
    reopened.heartbeat("a1", "t1", gen)                 # lease+generation survived


def test_create_task_duplicate_id_raises_conflict(tmp_path):
    import pytest
    store = mkstore(tmp_path)
    store.create_task("dup1", "first")
    with pytest.raises(coordd.Conflict):
        store.create_task("dup1", "second")
    # the failed insert must not have touched the original row
    assert store.tasks()[0]["title"] == "first"


def test_render_status_escapes_task_id(tmp_path):
    store = mkstore(tmp_path)
    store.create_task("t<script>x", "demo")
    out = store.render_status()
    assert "<script>" not in out
    assert "&lt;script&gt;" in out


class _NoRow:
    def fetchone(self):
        return None


class _FlakyConnection:
    """Stands in for a real sqlite3 connection (which is an immutable C type
    and cannot be monkeypatched) to force the IntegrityError branch of
    Store._event without needing an actual UNIQUE-constraint collision."""
    def execute(self, sql, params=()):
        if sql.startswith("INSERT INTO events"):
            raise sqlite3.IntegrityError("simulated non-idempotency-key failure")
        if sql.startswith("SELECT seq FROM events WHERE idempotency_key"):
            return _NoRow()
        raise AssertionError(f"unexpected query in test double: {sql}")


def test_event_integrity_error_with_none_key_reraises(tmp_path):
    """Defensive branch: an IntegrityError unrelated to idempotency-key collision
    (idempotency_key is None, so it cannot be the UNIQUE-constraint duplicate the
    except-clause was written for) must propagate, not crash on `row[0]` when the
    `WHERE idempotency_key=NULL` recovery lookup matches nothing."""
    import pytest
    store = mkstore(tmp_path)
    with pytest.raises(sqlite3.IntegrityError):
        store._event(_FlakyConnection(), "note", "a1", None, {}, None)
