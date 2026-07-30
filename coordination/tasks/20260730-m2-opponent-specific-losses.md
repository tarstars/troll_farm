# 20260730-m2-opponent-specific-losses: find active matchup-specific loss anomalies

- Status: result ready — `NO_ACTIONABLE_MATCHUP`; peer review pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER M2 / measurement
- Base commit: a4890910e4173a3114497e313052d2d5c99483d2
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T19:35:48Z
- Last updated UTC: 2026-07-30T19:46:13Z

## Outcome

Determine whether the exact resident has a statistically supported, materially negative,
currently active exact-opponent matchup after matching its own games on contemporaneous
strength, seat, map dimensions, resident score, and initial-tree count.

## Frozen protocol

`docs/m2-opponent-specific-losses-protocol-2026-07-30.md`.

## Exclusive write set

- `coordination/tasks/20260730-m2-opponent-specific-losses.md`
- `coordination/messages/local_codex_1/*-20260730-m2-opponent-specific-losses-*.md`
- `coordination/status/local_codex_1.md`
- `docs/m2-opponent-specific-losses-protocol-2026-07-30.md`
- `cgauto/opponent_specific_losses.py` (new)
- `tests/test_opponent_specific_losses.py` (new)
- `local_codex_1/m2-opponent-specific-losses/**`
- `data/analysis/live-agent-6553250/m2-opponent-specific-losses-*` (new)

The integrator may update canonical live docs and ledger volume 3 only at reviewed
closeout.

## Shared read-only paths

- Exact processed corpus and current leaderboard in the frozen protocol.
- `cgauto/roster_outcome_pricing.py`.
- N2 source/count result and M1's no-rating-rule result.
- Canonical STATE, CONSTRAINTS, BACKLOG, approach register, and ledgers.

## Do not touch

- `/home/tarstars/prj/troll_farm/data/`: exact reads only.
- `cgauto/live_loss_analysis.py` or any historical analyzer.
- `rust/src/bin/yamo_orchard_live.rs`.
- Raw replays/trajectories, sealed ranges, resident code, simulation, submission tooling,
  TestSession, or Arena state.
- Peer-owned N4 and evidence-index paths.
- Formatters over `rust/src/bin/` or `cgauto/`.

## Deliverables

- Frozen source/matching/multiplicity/actionability protocol and remotely published claim.
- Deterministic analyzer with synthetic matching/statistics/gate tests.
- Exact-identity eligibility table, matched residuals, uncertainty/multiplicity,
  preregistered sensitivities, and one verdict.
- Canonical result and follow-up boundary.

## Acceptance checks

- `python3 -m py_compile cgauto/opponent_specific_losses.py`
- `python3 cgauto/opponent_specific_losses.py --self-test`
- `python3 -m pytest -q tests/test_opponent_specific_losses.py`
- exact source hashes/counts, deterministic seed/output order, all gates explicit
- resident sacred SHA unchanged and no input/Arena writes

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Push implementation, tests, exact commands/hashes, full exact-opponent table, one verdict,
and any bounded replay-mechanism follow-up request. `chatgpt_1` reviews identification and
actionability before canonical integration.

## Implementation lock — 2026-07-30T19:40:54Z

- Analyzer SHA-256:
  `46d0a53ddadcf261cd2d2eb9a1ce8cf92fa3ffdb567c42a8008d2e3a992581dc`.
- Test SHA-256:
  `55b414c99ada11ae94e0ec0b5b9902f56c1217f36469575b6462673c38711bc6`.
- Compile/self-test/five tests pass.
- Preflight: 12 active identities clear games/seats; R1FA, a76a44, and BoatBuilder alone
  clear per-game matched-control support.

## Empirical result — 2026-07-30T19:46:13Z

- Verdict: **`NO_ACTIONABLE_MATCHUP`**.
- All 9,082 source records and the current leaderboard pass frozen count/hash gates.
- Three exact identities are primary-eligible; none clear all ten actionability gates.
- R1FA has the only stable negative hint (residual −31.621) but CI
  [−81.015,+22.243], Holm p 0.229, and win residual −0.087 fail the frozen gates.
- BoatBuilder's larger residual (−73.178) reverses by seat and is imprecise; a76a44 has a
  positive residual.
- Canonical result:
  `data/analysis/live-agent-6553250/m2-opponent-specific-losses-result-2026-07-30.md`.
- No identity-specific implementation, replay follow-up, resident change, or Arena action.
