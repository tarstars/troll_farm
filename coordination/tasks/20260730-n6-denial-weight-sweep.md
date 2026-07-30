# 20260730-n6-denial-weight-sweep: finish reproduction G1 once

- Status: active — implementation/source/dependency locked; development pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER N6 / H13 residual / reproduction G1
- Base commit: bf224757ddffe867799bd138814fc2669eb62ab9
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence; phase markers renew it
- Created UTC: 2026-07-30T20:47:30Z
- Last updated UTC: 2026-07-30T21:05:36Z

## Outcome

Run the one permitted nonzero denial-distance scalar sweep around the resident's guessed
900 weight, then either close the scalar line or produce a materially qualified candidate.

## Frozen protocol

`docs/n6-denial-weight-sweep-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-n6-denial-weight-sweep.md`
- `coordination/messages/local_codex_1/*-20260730-n6-denial-weight-sweep-*.md`
- `coordination/status/local_codex_1.md`
- `docs/n6-denial-weight-sweep-protocol-2026-07-30.md`
- `cgauto/n6_denial_weight_sweep.py` (new)
- `rust/src/bin/n6_denial_weight_sweep.rs` (new)
- `tests/test_n6_denial_weight_sweep.py` (new)
- `local_codex_1/n6-denial-weight-sweep/**`
- `data/analysis/live-agent-6553250/n6-denial-weight-sweep-*` (new)
- `artifacts/experiments/n6-denial-weight-sweep/**` (new, external-backed)

At empirical closeout the integrator may update canonical BACKLOG, approach register,
CONSTRAINTS, STATE, and the live ledger. No other shared path is authorized.

## Shared read-only paths

- Exact resident snapshot/dev source and A2-0b referee dependencies frozen in the protocol.
- Historical focus-bonus-off/capable-only record and H13 fidelity result.
- Existing eight opponent families, storage checker, trajectory schema, and waste detectors.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`,
  `rust/src/d171a_control_resident_snapshot.rs`, A2-0b locked source/results, or historical
  focus artifacts.
- `rust/src/game/mod.rs`, `rust/Cargo.toml`, raw games, cron, sealed/consumed ranges,
  submission tooling, TestSession, or Arena.
- Formatters over `rust/src/bin/` or `cgauto/`.

## Deliverables

- Remotely published protocol/claim before implementation.
- Fail-closed exact source materializer, isolated referee runner, analyzer, and tests.
- One-map smoke and dependency/source lock before development.
- Development selection or `CLOSED_AT_DEVELOPMENT`.
- If selected, separate published confirmation authorization, deterministic paired panel,
  trajectory/detector checks, all frozen gates, and one final verdict.
- Review handoff. No retune.

## Implementation lock

- Analyzer: `cgauto/n6_denial_weight_sweep.py`, SHA-256 `df9fb52e40b1f6a46df66dca09cf79e4cf95612a8970877b1b9b91ebb4ef5d85`.
- Runner: `rust/src/bin/n6_denial_weight_sweep.rs`, SHA-256 `548e814dea58f53373126836e32108f3409c62fae82d8fc09aaedf8e55e0376c`.
- Tests: `tests/test_n6_denial_weight_sweep.py`, SHA-256 `576a7e8eb2cdaee51595122211b8d5dba56ade25e10075d789178db29eed0960`.
- Generated module hashes: LOW `a827f7c1542f800e94f33b2e924a07d191b9e1c5a9202450744e81d5a75dee94`,
  CONTROL `9ac22932901aeff7d8c8855e54de23d5b9a83de6e4025bde5758f020b517ac03`,
  HIGH `bfba6c4be4bdeed7f8a30c375a30fefd63a8f91e294a53dd532af26a837040d6`.
- Dependency hashes remain the frozen resident `fff6669b`, referee `518c2228`, and
  continued mapgen `8e841958`.
- Release binary: `d1c17587458ebc5ec341321c37daac17d7a308680e90a4f5578dc8581170e821`.
- One-map jobs-1/jobs-4 TSVs are byte-identical at
  `10171ca6b3f514db1f7113de8fbd1f5a166b4e2f0a1f25725fe18280648b1cd9`;
  48/48 rows, zero critical/unclassified/opponent-command mismatches.
- The 48 trajectory records decode, have exact state/command alignment, and execute all
  six standing detectors without an exception.
- Ten focused tests and the analyzer self-test pass. No development panel has run.

## Arena authority

No platform access is needed or authorized by this task. A later qualified result requires
candidate packaging, peer promotion review, owner notification, and the full runbook.
