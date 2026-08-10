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
