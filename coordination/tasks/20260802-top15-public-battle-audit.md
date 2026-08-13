# 20260802-top15-public-battle-audit: rank immediately testable lessons from public top-15 games

- Status: in_progress
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: pending
- Integrator: local_codex_1
- Area: live-opponent reconnaissance / breadth strategy
- Base commit: 9e41a9d76a921207516f5b46b1b8dbd69ae466f5
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-08-02T18:47:18Z
- Last updated UTC: 2026-08-02T18:55:07Z

## Outcome

A timestamped, duplicate-aware audit of the publicly accessible recent battles for the
current top 15 Arena contestants, ending in a ranked list of concrete bot changes that can
be checked immediately against the exact stable/sector substrate.

## Frozen protocol

None. This is descriptive public-replay reconnaissance, not a promotion experiment. It may
form hypotheses but cannot qualify a candidate or consume sealed map ranges.

## Exclusive write set

- `scripts/top15_public_battle_audit.py`
- `data/analysis/live-agent-6553250/top15-public-battle-inventory-2026-08-02.json`
- `data/analysis/live-agent-6553250/top15-public-battle-audit-2026-08-02.json`
- `data/analysis/live-agent-6553250/top15-public-battle-audit-2026-08-02.md`
- `docs/reports/2026-08-02-top15-public-battle-audit.md`
- `coordination/tasks/20260802-top15-public-battle-audit.md`
- `coordination/messages/local_codex_1/*20260802-top15-public-battle-audit*`
- `coordination/status/local_codex_1.md`

## Shared read-only paths

- `cgauto/` platform clients and replay decoders
- `data/raw/games/` existing cache (read-only; no collection writes)
- `data/processed/` compact existing replay indexes
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, and the live ledger
- CodinGame public leaderboard and public battle endpoints

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred)
- `data/raw/games/` and the 05:17 collection cron
- sealed map ranges and confirmation blocks
- any Arena mutation endpoint

## Deliverables

- Reproducible snapshot containing top-15 identity/rank/score and accessible battle ids.
- Duplicate-aware per-player and pooled behavioral measurements with explicit support.
- Ranked `test now` ideas separated from observations and causal claims.
- Limitations covering changing bot versions, last-battle selection, and incomplete access.

## Acceptance checks

- `/home/tarstars/prj/troll_farm/.venv/bin/python scripts/top15_public_battle_audit.py --help` exits zero.
- Re-running the analyzer on its captured compact input reproduces the reported aggregates.
- Every ranked idea cites players, battle support, and a falsifiable local check.
- `git diff --exit-code -- rust/src/bin/yamo_orchard_live.rs data/raw/games/` is empty.

## Arena authority

Read-only platform access: allowed by standing policy. Public leaderboard/replay reads only.
Platform mutation: forbidden; this task does not submit agents or start TestSession games.

## Handoff

Pushed script, compact evidence JSON, detailed report, validation transcript, and explicit
statement that the audit is descriptive rather than candidate-qualification evidence.
