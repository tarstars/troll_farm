# 20260730-m3-seat-asymmetry: audit exact resident seat effects

- Status: claimed — frozen protocol published; implementation pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER M3 / measurement
- Base commit: b9aec2b00ac8ba1a12bac390bf3292e491c151c5
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T19:48:51Z
- Last updated UTC: 2026-07-30T19:48:51Z

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
