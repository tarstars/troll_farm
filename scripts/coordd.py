#!/usr/bin/env python3
"""coordd — coordination control plane (spec: docs/superpowers/specs/
2026-08-10-coordination-control-plane-design.md). Single file, stdlib only.
Store = all semantics over SQLite (WAL). HTTP layer and CLI modes are added in
later tasks of the same plan; keep them thin — semantics live here so they are
testable without a socket."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import sqlite3

TASK_STATES = ("open", "claimed", "review", "blocked", "done", "dropped")

SCHEMA = """
CREATE TABLE IF NOT EXISTS agents(
  id TEXT PRIMARY KEY, role TEXT NOT NULL DEFAULT 'contributor',
  tool_digest TEXT, protocol_version INTEGER NOT NULL,
  capabilities TEXT NOT NULL DEFAULT '[]', last_seen TEXT NOT NULL,
  compatible INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(
  id TEXT PRIMARY KEY, title TEXT NOT NULL,
  state TEXT NOT NULL CHECK(state IN
    ('open','claimed','review','blocked','done','dropped')),
  priority INTEGER NOT NULL DEFAULT 2, owner TEXT,
  created TEXT NOT NULL, updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS task_paths(
  task_id TEXT NOT NULL, prefix TEXT NOT NULL, PRIMARY KEY(task_id, prefix));
CREATE TABLE IF NOT EXISTS leases(
  task_id TEXT PRIMARY KEY, owner TEXT NOT NULL, generation INTEGER NOT NULL,
  expires TEXT NOT NULL, last_heartbeat TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(
  seq INTEGER PRIMARY KEY AUTOINCREMENT, server_time TEXT NOT NULL,
  type TEXT NOT NULL, actor TEXT NOT NULL, task_id TEXT,
  payload TEXT NOT NULL DEFAULT '{}', idempotency_key TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS acks(
  event_seq INTEGER NOT NULL, agent TEXT NOT NULL, server_time TEXT NOT NULL,
  PRIMARY KEY(event_seq, agent));
CREATE TABLE IF NOT EXISTS artifacts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
  generation INTEGER NOT NULL, git_ref TEXT NOT NULL, commit_hex TEXT NOT NULL,
  paths TEXT NOT NULL, verified INTEGER NOT NULL, server_time TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reviews(
  id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
  reviewer TEXT NOT NULL, verdict TEXT NOT NULL, evidence TEXT,
  artifact_generation INTEGER, server_time TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


class CoordError(Exception):
    status = 400


class Denied(CoordError):
    status = 403


class NotFound(CoordError):
    status = 404


class Conflict(CoordError):
    status = 409


class Unverifiable(CoordError):
    status = 422


class Store:
    PROTOCOL_VERSION = 1
    LEASE_TTL = 900  # seconds; spec §3: 15-minute lease

    def __init__(self, db_path, repo_dir=None, now=None):
        self.db_path = db_path
        self.repo_dir = repo_dir
        self._now = now or (lambda: datetime.now(timezone.utc))
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript(SCHEMA)
        con.commit()
        con.close()

    def _now_iso(self):
        return self._now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @contextmanager
    def _tx(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.execute("PRAGMA busy_timeout=10000")
        try:
            con.execute("BEGIN IMMEDIATE")
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def _read(self):
        con = sqlite3.connect(self.db_path, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def register(self, agent, role="contributor", tool_digest=None,
                 protocol_version=1, capabilities=()):
        compatible = int(protocol_version == self.PROTOCOL_VERSION)
        with self._tx() as con:
            con.execute(
                "INSERT INTO agents(id, role, tool_digest, protocol_version,"
                " capabilities, last_seen, compatible)"
                " VALUES(?,?,?,?,?,?,?)"
                " ON CONFLICT(id) DO UPDATE SET role=excluded.role,"
                " tool_digest=excluded.tool_digest,"
                " protocol_version=excluded.protocol_version,"
                " capabilities=excluded.capabilities,"
                " last_seen=excluded.last_seen, compatible=excluded.compatible",
                (agent, role, tool_digest, protocol_version,
                 json.dumps(list(capabilities)), self._now_iso(), compatible))
        return {"agent": agent, "compatible": bool(compatible)}

    def create_task(self, task_id, title, priority=2):
        now = self._now_iso()
        with self._tx() as con:
            con.execute(
                "INSERT INTO tasks(id, title, state, priority, created, updated)"
                " VALUES(?,?,?,?,?,?)",
                (task_id, title, "open", priority, now, now))
        return {"task_id": task_id, "state": "open"}

    def set_state(self, task_id, state, actor):
        if state not in TASK_STATES:
            raise CoordError(f"unknown state {state!r}; allowed: {TASK_STATES}")
        with self._tx() as con:
            cur = con.execute("UPDATE tasks SET state=?, updated=? WHERE id=?",
                              (state, self._now_iso(), task_id))
            if cur.rowcount == 0:
                raise NotFound(f"no task {task_id!r}")
            self._event(con, "state", actor, task_id, {"state": state})
        return {"task_id": task_id, "state": state}

    def tasks(self, state=None):
        con = self._read()
        try:
            q = "SELECT * FROM tasks" + (" WHERE state=?" if state else "")
            rows = con.execute(q, (state,) if state else ()).fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()

    @staticmethod
    def _overlap(a, b):
        return a.startswith(b) or b.startswith(a)

    def _require_agent(self, con, agent):
        row = con.execute("SELECT compatible FROM agents WHERE id=?",
                          (agent,)).fetchone()
        if row is None or not row[0]:
            raise Denied(f"agent {agent!r} not registered as compatible"
                         f" (protocol {self.PROTOCOL_VERSION} required)")

    def claim(self, agent, task_id, prefixes, idempotency_key=None):
        if not prefixes:
            raise CoordError("a claim must declare at least one write-set prefix")
        now = self._now_iso()
        with self._tx() as con:
            self._require_agent(con, agent)
            trow = con.execute("SELECT id FROM tasks WHERE id=?", (task_id,)).fetchone()
            if trow is None:
                raise NotFound(f"no task {task_id!r}")
            lease = con.execute(
                "SELECT owner, generation, expires FROM leases WHERE task_id=?",
                (task_id,)).fetchone()
            if lease and lease[2] > now and lease[0] != agent:
                raise Conflict(f"task {task_id!r} owned by {lease[0]}"
                               f" until {lease[2]} (gen {lease[1]})")
            for other_task, prefix in con.execute(
                    "SELECT l.task_id, tp.prefix FROM leases l"
                    " JOIN task_paths tp ON tp.task_id = l.task_id"
                    " WHERE l.task_id != ? AND l.expires > ?", (task_id, now)):
                if any(self._overlap(p, prefix) for p in prefixes):
                    raise Conflict(f"write-set overlap: {prefix!r} held by"
                                   f" active task {other_task!r}")
            gen = (lease[1] + 1) if lease else 1
            expires = (self._now() + timedelta(seconds=self.LEASE_TTL)) \
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            con.execute("INSERT OR REPLACE INTO leases VALUES(?,?,?,?,?)",
                        (task_id, agent, gen, expires, now))
            con.execute("DELETE FROM task_paths WHERE task_id=?", (task_id,))
            con.executemany("INSERT INTO task_paths VALUES(?,?)",
                            [(task_id, p) for p in prefixes])
            con.execute("UPDATE tasks SET state='claimed', owner=?, updated=?"
                        " WHERE id=?", (agent, now, task_id))
            self._event(con, "claim", agent, task_id,
                        {"generation": gen, "prefixes": list(prefixes)},
                        idempotency_key)
        return {"task_id": task_id, "generation": gen, "expires": expires}

    RELEASE_OUTCOMES = ("open", "review", "blocked", "done", "dropped")

    def _require_lease(self, con, agent, task_id, generation):
        row = con.execute(
            "SELECT owner, generation, expires FROM leases WHERE task_id=?",
            (task_id,)).fetchone()
        if row is None:
            raise Conflict(f"no lease on {task_id!r}")
        owner, gen, expires = row
        if owner != agent or gen != generation:
            raise Conflict(f"stale generation for {task_id!r}: lease is"
                           f" {owner}@gen{gen}, caller {agent}@gen{generation}")
        if expires <= self._now_iso():
            raise Conflict(f"lease on {task_id!r} expired at {expires}")

    def heartbeat(self, agent, task_id, generation):
        now = self._now_iso()
        with self._tx() as con:
            self._require_lease(con, agent, task_id, generation)
            expires = (self._now() + timedelta(seconds=self.LEASE_TTL)) \
                .strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            con.execute("UPDATE leases SET expires=?, last_heartbeat=?"
                        " WHERE task_id=?", (expires, now, task_id))
        return {"expires": expires}

    def release(self, agent, task_id, generation, outcome):
        if outcome not in self.RELEASE_OUTCOMES:
            raise CoordError(f"outcome {outcome!r} not in {self.RELEASE_OUTCOMES}")
        with self._tx() as con:
            self._require_lease(con, agent, task_id, generation)
            con.execute("DELETE FROM leases WHERE task_id=?", (task_id,))
            owner = None if outcome in ("open", "dropped") else agent
            con.execute("UPDATE tasks SET state=?, owner=?, updated=? WHERE id=?",
                        (outcome, owner, self._now_iso(), task_id))
            self._event(con, "release", agent, task_id,
                        {"generation": generation, "outcome": outcome})
        return {"task_id": task_id, "state": outcome}

    def _event(self, con, type_, actor, task_id, payload, idempotency_key=None):
        try:
            cur = con.execute(
                "INSERT INTO events(server_time, type, actor, task_id, payload,"
                " idempotency_key) VALUES(?,?,?,?,?,?)",
                (self._now_iso(), type_, actor, task_id,
                 json.dumps(payload or {}), idempotency_key))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            row = con.execute("SELECT seq FROM events WHERE idempotency_key=?",
                              (idempotency_key,)).fetchone()
            return row[0]

    def add_event(self, actor, type_, task_id=None, payload=None,
                  idempotency_key=None):
        with self._tx() as con:
            seq = self._event(con, type_, actor, task_id, payload, idempotency_key)
        return {"seq": seq}

    def events(self, since=0):
        con = self._read()
        try:
            rows = con.execute(
                "SELECT * FROM events WHERE seq > ? ORDER BY seq", (since,)).fetchall()
            out = []
            for r in rows:
                d = dict(r)
                d["payload"] = json.loads(d["payload"])
                out.append(d)
            return out
        finally:
            con.close()

    def ack(self, agent, event_seq):
        with self._tx() as con:
            if con.execute("SELECT 1 FROM events WHERE seq=?",
                           (event_seq,)).fetchone() is None:
                raise NotFound(f"no event {event_seq}")
            con.execute("INSERT OR IGNORE INTO acks VALUES(?,?,?)",
                        (event_seq, agent, self._now_iso()))
        return {"ok": True}

    def add_review(self, task_id, reviewer, verdict, evidence=None,
                   artifact_generation=None):
        with self._tx() as con:
            con.execute(
                "INSERT INTO reviews(task_id, reviewer, verdict, evidence,"
                " artifact_generation, server_time) VALUES(?,?,?,?,?,?)",
                (task_id, reviewer, verdict, evidence, artifact_generation,
                 self._now_iso()))
            self._event(con, "review", reviewer, task_id, {"verdict": verdict})
        return {"ok": True}

    def reviews(self, task_id):
        con = self._read()
        try:
            return [dict(r) for r in con.execute(
                "SELECT * FROM reviews WHERE task_id=? ORDER BY id", (task_id,))]
        finally:
            con.close()
