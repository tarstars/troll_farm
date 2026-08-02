# 20260802-live-ladder-state-read: current health of resident 6585846

- Status: BLOCKED — this checkout cannot perform live platform reads (no credentials, no host data)
- Record owner: claude_1
- Work owner: claude_1
- Reviewer: local_codex_1
- Integrator: local_codex_1
- Area: live monitoring of the sole Arena leg (B3.16, `docs/STATE.md` §1/§4)
- Base commit: `8306fa7d2897014f915e950b33128c0c38e05b1a`
- Branch: agent/claude_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-08-02T05:39:00Z
- Last updated UTC: 2026-08-02T05:45:00Z

## Outcome

A timed read-only health read of live agent `6585846` / submission `41071360` — score,
rank, finished-game count, catastrophe rate, identity cleanliness — compared against the
last recorded read (2026-07-31T08:56:52Z, 16.97 at rank 95/113, 11/11 parsed, one pending)
and against the B3.12 historical comparator (22.99 at rank 34/113 over 160 clean games).

Owner-directed on 2026-08-01. Read-only platform work, authorized for any agent by
`docs/STATE.md` §3. **No submission, no TestSession, no restore, no candidate.**

## Frozen protocol

None. `docs/PROMOTION-RUNBOOK.md` §3 supplies the sanctioned read tooling.

## Exclusive write set

- `coordination/tasks/20260802-live-ladder-state-read.md`
- `coordination/messages/claude_1/`
- `coordination/status/claude_1.md`

## Shared read-only paths

- `cgauto/cg_rank.py`, `cgauto/battles.py`, `cgauto/arena_transfer_checkpoint.py`
- `docs/PROMOTION-RUNBOOK.md`, `docs/STATE.md`

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred, no compile-then-restore declared here)
- `cgauto/api_submit.py` and every submission path — this task performs no mutation
- `data/raw/games/`, the 05:17 cron, sealed map ranges

## Deliverables

- A timestamped read logged to this record and to a `result` message, or — as happened —
  an explicit blocker naming exactly what is unavailable.

## Acceptance checks

- `python3 cgauto/arena_transfer_checkpoint.py --agent-id 6585846 --submission-id 41071360
  --role live` — one summary line, `identity_clean` true, exit 0.
- `python3 cgauto/cg_rank.py` — authoritative `ARENA-ROOM` line.

## Blocking finding (2026-08-02)

This working copy is **a fresh clone on a cloud VM, not the project host**. `.git` was
created 2026-08-01T19:27:45Z and the reflog holds exactly one entry: `clone: from
github.com:tarstars/troll_farm.git`. Consequences, each verified:

1. **No platform credentials.** `cgauto/cg_session.txt` does not exist, so `battles.py` and
   `arena_transfer_checkpoint.py` (via `battle_taxonomy`) raise `FileNotFoundError` at
   import, and `cg_rank.py` has no cookie to send. The file is correctly ignored by
   `cgauto/.gitignore:3` and has never been tracked — this is intended secret hygiene, not
   a repository fault. Network is not the problem: `https://www.codingame.com/` is
   reachable from here.
2. **No Python environment.** `cg_rank.py` also fails on `ModuleNotFoundError: No module
   named 'codingame'`; `uv sync` has not been run in this clone.
3. **No collection cron.** `crontab -l` reports `no crontab for tarstars`. The 05:17 daily
   collection that `docs/STATE.md` §1 credits with a compounding 9,082-game corpus does
   **not** run on this machine.
4. **No bulk data.** The `medium_data` volume is unmounted
   (`cgauto/check_external_storage.py` → `no mounted filesystem with label 'medium_data'`),
   so `artifacts/`, `outputs/`, `data/generated/`, `data/external/` are absent, as is
   `data/raw/snapshots/` (host-only; 325 files under `data/raw/` are tracked, the snapshot
   corpus is not among them).
5. **The one local leaderboard artifact is stale.** `data/raw/leaderboard.json` holds 1,000
   rows whose `tass` entry is agent `6561795` at 22.18, rank 40 — the pre-B3.12 resident.
   It predates every agent in the current chain and is not a substitute for a live read.

## Handoff

Unblocking requires exactly one of:

- the owner placing a valid `cgauto/cg_session.txt` on this machine (safe: gitignored,
  never tracked, must not be pasted into chat or committed) plus `uv sync`; or
- the read being executed on the project host by `local_codex_1`, with the result published
  to a message this record can cite.

Until then the live health of `6585846` is **unknown to this agent**, and the last
authoritative datum stays the 2026-07-31T08:56:52Z read of 16.97 at rank 95/113.
