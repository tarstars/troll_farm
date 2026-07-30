# 20260730-n5-endgame-opponent-plant-contest: quantify the missing endgame contest mechanic

- Status: active — protocol frozen; implementation pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: BACKLOG N5 / H13 residual
- Base commit: 50eca900a2edcc669f29b05b99781e8e113839ec
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T20:30:00Z
- Last updated UTC: 2026-07-30T20:30:00Z

## Outcome

Reconstruct the exact late opponent-created crop generations counted directionally by H13,
measure subsequent subject/opponent extraction and optimistic subject access, and decide
whether the replay-conditioned observed-yield opportunity can clear 20 margin per resident
game.

## Frozen protocol

`docs/n5-endgame-opponent-plant-contest-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-n5-endgame-opponent-plant-contest.md`
- `coordination/messages/local_codex_1/*-20260730-n5-endgame-opponent-plant-contest-*.md`
- `coordination/status/local_codex_1.md`
- `docs/n5-endgame-opponent-plant-contest-protocol-2026-07-30.md`
- `cgauto/endgame_opponent_plant_contest.py` (new)
- `tests/test_endgame_opponent_plant_contest.py` (new)
- `local_codex_1/n5-endgame-opponent-plant-contest/**`
- `data/analysis/live-agent-6553250/n5-endgame-opponent-plant-contest-*` (new)

At empirical closeout the integrator may update `docs/BACKLOG.md`,
`docs/APPROACH-REGISTER-2026-07-30.md`, `docs/CONSTRAINTS.md`, `docs/STATE.md`, and the
live ledger named by STATE §5. No other shared path is authorized.

## Shared read-only paths

- Exact processed/raw/trajectory corpus and dependencies frozen in the protocol.
- H13 task/analyzer/result ledger record, verified mechanics, resident sacred source.
- N2 generation-lineage analyzer/result and H3 causal constraints.
- Canonical live docs and ledger.

## Do not touch

- Any existing file under `/home/tarstars/prj/troll_farm/data/`: exact reads only.
- Historical analyzers or generated results.
- `rust/src/bin/yamo_orchard_live.rs`.
- Raw replays/trajectories, sealed ranges, resident code, simulation, submission tooling,
  TestSession, or Arena state.
- Peer-owned N4 and evidence-index paths.
- Formatters over `rust/src/bin/` or `cgauto/`.

## Deliverables

- Frozen, remotely published protocol/claim before implementation.
- Deterministic analyzer with synthetic lineage/outcome/access/bootstrap/verdict tests.
- Exact 382-game input manifest, target-generation table, compact result, and report.
- One of `MATERIAL_CONTEST_OPPORTUNITY`, `NO_MATERIAL_CONTEST_OPPORTUNITY`, or
  `UNIDENTIFIABLE`, with every gate explicit.
- Review handoff preserving the observational and carried-resource boundaries.

## Acceptance checks

- `python3 -m py_compile cgauto/endgame_opponent_plant_contest.py`
- `python3 cgauto/endgame_opponent_plant_contest.py --self-test`
- `python3 -m pytest -q tests/test_endgame_opponent_plant_contest.py`
- exact source/dependency/cohort hashes and 382/382 decode coverage
- target identity agrees in both lineage orientations
- deterministic seed/order/output and resident sacred SHA unchanged
- no input, policy, simulation, or Arena writes

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Push implementation, tests, exact commands/hashes, all event/value/access/gate counts, and
one verdict. A material verdict requests a separately frozen controlled-simulation
proposal; no other continuation is automatic.
