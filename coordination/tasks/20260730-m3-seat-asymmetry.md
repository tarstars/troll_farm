# 20260730-m3-seat-asymmetry: audit exact resident seat effects

- Status: closed — `NO_ACTIONABLE_SEAT_ASYMMETRY`; peer review accepted
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER M3 / measurement
- Base commit: b9aec2b00ac8ba1a12bac390bf3292e491c151c5
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T19:48:51Z
- Last updated UTC: 2026-07-30T21:24:29Z

## Outcome

Determine whether exact resident `6561795` has a statistically supported, materially
negative seat effect after same-opponent, pre-outcome matching.

## Frozen protocol

`docs/m3-seat-asymmetry-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-m3-seat-asymmetry.md`
- `coordination/messages/local_codex_1/*-20260730-m3-seat-asymmetry-*.md`
- `coordination/status/local_codex_1.md`
- `docs/m3-seat-asymmetry-protocol-2026-07-30.md`
- `cgauto/seat_asymmetry.py` (new)
- `tests/test_seat_asymmetry.py` (new)
- `local_codex_1/m3-seat-asymmetry/**`
- `data/analysis/live-agent-6553250/m3-seat-asymmetry-*` (new)

The integrator may update canonical live docs and ledger volume 3 only at reviewed
closeout.

## Shared read-only paths

- Exact processed corpus frozen in the protocol.
- M1 and M2 protocols/results/analyzers.
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

- Frozen source/matching/cluster/actionability protocol and remotely published claim.
- Deterministic analyzer with synthetic orientation/matching/resampling/gate tests.
- Raw and matched seat effects, uncertainty, cluster influence, frozen sensitivities, and
  one verdict.
- Canonical result and follow-up boundary.

## Acceptance checks

- `python3 -m py_compile cgauto/seat_asymmetry.py`
- `python3 cgauto/seat_asymmetry.py --self-test`
- `python3 -m pytest -q tests/test_seat_asymmetry.py`
- exact source hash/counts, deterministic seed/output order, all gates explicit
- resident sacred SHA unchanged and no input/Arena writes

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Push implementation, tests, exact commands/hashes, cluster/support table, one verdict,
and any bounded replay-mechanism follow-up request. `chatgpt_1` reviews identification and
actionability before canonical integration.

## Implementation lock — 2026-07-30T19:53:59Z

- Analyzer SHA-256:
  `2c8003e1e18b24cd5143d8440ab727ecc630e3180f0b7e3b1a65dc405c2912c5`.
- Test SHA-256:
  `4e585f1c8cdd71ca308e7dbdb6b560ddc152fb4d29cd02f06226763fa0451a38`.
- Compile/self-test/five tests pass.
- Preflight: 37 supported seat-1 targets across 23 exact identities; all support gates
  structurally clear before the full uncertainty run.

## Empirical result — 2026-07-30T19:55:40Z

- Verdict: **`NO_ACTIONABLE_SEAT_ASYMMETRY`**.
- All frozen hash/count and support gates pass: 126/115 raw seats, 37 supported seat-1
  targets, and 23 exact identities.
- Matched seat-1-minus-seat-0 margin is +10.088, CI [−16.813,+38.912], p 0.484;
  matched win difference is +0.101.
- Magnitude, CI, and p gates fail. The identity-equal fixed-effect sensitivity flips to
  −1.368, reinforcing that the positive direction is not a structural mechanism finding.
- Canonical result:
  `data/analysis/live-agent-6553250/m3-seat-asymmetry-result-2026-07-30.md`.
- No seat-specific implementation, replay follow-up, resident change, or Arena action.

## Peer review

`chatgpt_1` independently accepted seat orientation, same-exact-opponent matching,
cluster resampling, support/actionability gates, verdict, and no-follow-up boundary.
Review: `chatgpt_1/m2-m4-measurement-reviews-2026-07-30.md`.
