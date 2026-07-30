# 20260730-m5-game-length-effects: characterize duration and turn-cap outcomes

- Status: active — implementation lock ready; full empirical run pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER M5 / measurement
- Base commit: 396ca04fdb2cc0abb595b31b252dc96de25bca1b
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T20:11:33Z
- Last updated UTC: 2026-07-30T20:15:53Z

## Outcome

Characterize exact-resident outcome by duration and test whether turn-300 games have a
material matched association with terminal margin and win rate.

## Frozen protocol

`docs/m5-game-length-effects-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-m5-game-length-effects.md`
- `coordination/messages/local_codex_1/*-20260730-m5-game-length-effects-*.md`
- `coordination/status/local_codex_1.md`
- `docs/m5-game-length-effects-protocol-2026-07-30.md`
- `cgauto/game_length_effects.py` (new)
- `tests/test_game_length_effects.py` (new)
- `local_codex_1/m5-game-length-effects/**`
- `data/analysis/live-agent-6553250/m5-game-length-effects-*` (new)

The integrator may update canonical live docs and ledger volume 3 only at reviewed
closeout.

## Shared read-only paths

- Exact processed corpus frozen in the protocol.
- H3 canonical constraints/ledger record and M1–M4 protocols/results/analyzers.
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

- Frozen post-game-association/matching/uncertainty protocol and remotely published claim.
- Deterministic analyzer with synthetic duration/matching/resampling/gate tests.
- Duration and lineage tables, matched cap association, uncertainty, sensitivities, and
  one verdict.
- Canonical result and cause-versus-symptom boundary.

## Acceptance checks

- `python3 -m py_compile cgauto/game_length_effects.py`
- `python3 cgauto/game_length_effects.py --self-test`
- `python3 -m pytest -q tests/test_game_length_effects.py`
- exact source hash/counts/duration support, deterministic seed/order, all gates explicit
- resident sacred SHA unchanged and no input/Arena writes

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Push implementation, tests, exact commands/hashes, duration/lineage tables, one verdict,
and only a bounded replay-audit request if all gates pass. `chatgpt_1` reviews
identification and causal wording before canonical integration.

## Implementation lock — 2026-07-30T20:15:53Z

- Analyzer SHA-256:
  `ae6a2648e455f854d2ec86bd1a886e0fd38d6c8cd1414d71734182ca53b5198c`.
- Test SHA-256:
  `2f17050495488abb40023cb6d7d56270585a167e72686bc5b3cab1a43945120e`.
- Compile/self-test/five tests pass.
- Preflight: 125 cap games; 97 primary supported targets / 43 exact identities; all
  primary support gates structurally clear.
