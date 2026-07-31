# 20260730-n5-endgame-opponent-plant-contest: quantify the missing endgame contest mechanic

- Status: empirical arithmetic supported; review blocked pending protocol correction
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: BACKLOG N5 / H13 residual
- Base commit: 50eca900a2edcc669f29b05b99781e8e113839ec
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T20:30:00Z
- Last updated UTC: 2026-07-31T12:58:00Z

## Independent review

`chatgpt_1` supports the reported population and ceiling arithmetic but withholds canonical
acceptance until (1) the frozen synthetic semantic-test obligations are covered and
(2) `subject_eta_at_birth` is corrected to the literal birth state or explicitly frozen,
renamed, and tested as a pre-PLANT convention. No successor experiment follows before a
narrow corrected re-review.

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

## Implementation lock — 2026-07-30T20:36:30Z

- Analyzer SHA-256:
  `f2075297ae24631714abfe3b6d92b7fc357dad17228a237cf73d36c2beedcd2d`.
- Test SHA-256:
  `947951899951440d4d86493df94e61841bf62dee4ec1a506d451f0eaac5699e6`.
- Compile and self-test pass; six focused tests pass.
- Sacred resident SHA remains
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- The full 382-occurrence audit has not been run at this lock.

## Empirical result — 2026-07-30T20:39:00Z

- Verdict: **`NO_MATERIAL_CONTEST_OPPORTUNITY`**.
- Exact coverage: 382/382 cohort occurrences, 381 unique games, zero decode or target
  integrity failures.
- H13 reproduces exactly: resident 388 generations / 78 of 170 reaching games; yamo 205
  / 37 of 103.
- The resident factor-two replay-conditioned observed-yield ceiling is 11.9917 per all
  242 games, whole-game bootstrap 95% CI [8.7273, 15.7603], below 20.
- Opponent extracted value is 1,487 versus resident 241; only 51/388 targets are contacted,
  but carried extraction is not banked score and changed-policy causality is unidentified.
- All source, support, and no-material gates pass. No simulation, resident, or Arena action.
- Canonical result:
  `data/analysis/live-agent-6553250/n5-endgame-opponent-plant-contest-result-2026-07-30.md`.
