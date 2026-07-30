# 20260730-n6-denial-weight-sweep: finish reproduction G1 once

- Status: active — protocol frozen; implementation pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER N6 / H13 residual / reproduction G1
- Base commit: bf224757ddffe867799bd138814fc2669eb62ab9
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence; phase markers renew it
- Created UTC: 2026-07-30T20:47:30Z
- Last updated UTC: 2026-07-30T20:47:30Z

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

## Arena authority

No platform access is needed or authorized by this task. A later qualified result requires
candidate packaging, peer promotion review, owner notification, and the full runbook.
