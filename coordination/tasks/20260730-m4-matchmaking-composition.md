# 20260730-m4-matchmaking-composition: audit resident opponent mix and drift

- Status: active — implementation lock ready; full empirical run pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER M4 / measurement
- Base commit: 25dce522ecab58fca111d2550863aa6bdd571d2b
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T19:59:19Z
- Last updated UTC: 2026-07-30T20:04:31Z

## Outcome

Describe the exact resident's opponent mix and determine whether its newest 60 matchups
are materially stronger or weaker than its oldest 60.

## Frozen protocol

`docs/m4-matchmaking-composition-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-m4-matchmaking-composition.md`
- `coordination/messages/local_codex_1/*-20260730-m4-matchmaking-composition-*.md`
- `coordination/status/local_codex_1.md`
- `docs/m4-matchmaking-composition-protocol-2026-07-30.md`
- `cgauto/matchmaking_composition.py` (new)
- `tests/test_matchmaking_composition.py` (new)
- `local_codex_1/m4-matchmaking-composition/**`
- `data/analysis/live-agent-6553250/m4-matchmaking-composition-*` (new)

The integrator may update canonical live docs and ledger volume 3 only at reviewed
closeout.

## Shared read-only paths

- Exact processed corpus and current leaderboard frozen in the protocol.
- M1–M3 protocols/results/analyzers.
- Canonical STATE, CONSTRAINTS, BACKLOG, approach register, and ledgers.

## Do not touch

- `/home/tarstars/prj/troll_farm/data/`: exact reads only.
- Historical analyzers or generated results.
- `rust/src/bin/yamo_orchard_live.rs`.
- Raw replays/trajectories, sealed ranges, resident code, simulation, submission tooling,
  TestSession, or Arena state.
- Peer-owned N4 and evidence-index paths.
- Formatters over `rust/src/bin/` or `cgauto/`.

## Deliverables

- Frozen endpoint/composition/uncertainty/drift protocol and remotely published claim.
- Deterministic analyzer with synthetic chronology/block-bootstrap/identity/gate tests.
- Opponent frequency/concentration table, endpoint contrasts, uncertainty, sensitivities,
  and one verdict.
- Canonical result and surveillance boundary.

## Acceptance checks

- `python3 -m py_compile cgauto/matchmaking_composition.py`
- `python3 cgauto/matchmaking_composition.py --self-test`
- `python3 -m pytest -q tests/test_matchmaking_composition.py`
- exact source hashes/counts, deterministic seed/output order, all gates explicit
- resident sacred SHA unchanged and no input/Arena writes

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Push implementation, tests, exact commands/hashes, opponent table, one verdict, and any
bounded surveillance update. `chatgpt_1` reviews identification and drift inference before
canonical integration.

## Implementation lock — 2026-07-30T20:04:31Z

- Analyzer SHA-256:
  `47ac0dd9ad0ab96bc05f80c321219ea16c73fab7254fc9df0553d71eb538e4b3`.
- Test SHA-256:
  `776c3a67052f318e7695015c67e72d2ec5e93e549115e8a28c932b647d04b286`.
- Compile/self-test/five tests pass.
- Preflight: exact 241-game resident panel and 60/60 endpoints; smoke-run source,
  chronology, identity-lineage, and output paths pass.
