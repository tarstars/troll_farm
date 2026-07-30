# 20260730-x1-mechanics-rederivation: source-backed mechanics conformance audit

- Status: active
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER X1 / mechanics and platform
- Base commit: 32534678c3d4b86962ebcb5909cc9dfa25223abb
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-07-30T14:56:59Z
- Last updated UTC: 2026-07-30T15:02:22Z

## Outcome

A primary-source-backed inventory of referee mechanics, with executable regression or
differential checks against the maintained Python/Rust simulation paths. Every audited
mechanic is classified MATCH, MISMATCH, or UNTESTED, and every mismatch is scoped for its
effect on past evidence and A2 before the parity harness starts.

## Frozen protocol

None. This is a read-only audit of existing mechanics and implementations. It may add
tests and documentation, but it may not alter simulator semantics until a mismatch is
recorded with primary-source evidence and its affected population is identified.

## Exclusive write set

- `cgauto/mechanics_rederivation_audit.py` (new)
- `tests/test_mechanics_rederivation.py` (new)
- `docs/reviews/2026-07-30-local_codex_1-x1-mechanics-rederivation.md` (new)
- `coordination/tasks/20260730-x1-mechanics-rederivation.md`
- `coordination/status/local_codex_1.md`
- `coordination/messages/local_codex_1/`
- `local_codex_1/`

Conditional integrator-only closeout paths, serialized against N1 integration:

- `docs/mechanics.md`
- `docs/APPROACH-REGISTER-2026-07-30.md`
- `docs/STATE.md`
- `docs/CONSTRAINTS.md`
- `data/analysis/live-agent-6553250/legend-top3-experiment-cycle-vol2-2026-07-23.md`

## Shared read-only paths

- Primary referee source at a recorded upstream commit
- `rust/src/game/**`
- `sim/**`
- existing mechanics/parity tests and result records
- open replay-derived summaries, excluding sealed ranges

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`
- `rust/src/bin/**` and `cgauto/**` formatting
- sealed map/game ranges
- `data/raw/games/` and the 05:17 collection cron
- Arena, TestSession, submission tooling, or live platform state

## Deliverables

- Source/implementation conformance matrix covering initialization, map generation,
  movement/collisions, task ordering and legality, resource actions, training, plant
  lifecycle, scoring, and termination.
- Regression checks for every newly documented or corrected rule that can affect A2.
- Impact statement naming any past findings that require re-analysis.

## Acceptance checks

- `python3 -m pytest -q tests/test_mechanics_rederivation.py`
- Relevant existing Python and Rust engine/map-generation suites remain green.
- The resident dev-copy SHA-256 still begins `fff6669b`.
- Every MATCH/MISMATCH claim cites an upstream commit plus exact referee class/method.
- No unexplained mismatch remains on an A2-critical mechanic; UNTESTED items are explicit.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Pushed report, tests, exact validation output, impact assessment, and a handoff to
`chatgpt_1`; shared-ledger/state updates are integrated only after the verdict is stable.
