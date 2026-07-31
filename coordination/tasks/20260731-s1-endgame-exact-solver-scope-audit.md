# 20260731-s1-endgame-exact-solver-scope-audit

- Status: active — claim/protocol publication pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER S1 / endgame exact solver
- Base commit: 8dc2f9d13b13c8cf8ccbb20d3964ac2539ee5288
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T00:13:34Z
- Last updated UTC: 2026-07-31T00:13:34Z

## Outcome

Determine whether a full exact last-N-turn solver is distinct, well-posed, and bounded
enough to justify a later implementation protocol.

## Frozen protocol

`docs/s1-endgame-exact-solver-scope-protocol-2026-07-31.md`.

## Exclusive write set

- this task record;
- `coordination/messages/local_codex_1/*-20260731-s1-endgame-solver-*.md`;
- `coordination/status/local_codex_1.md`;
- `cgauto/s1_endgame_solver_feasibility.py` (new);
- `tests/test_s1_endgame_solver_feasibility.py` (new);
- `data/analysis/live-agent-6553250/s1-endgame-solver-*` (new);
- `local_codex_1/s1-endgame-solver-feasibility/` (new, compact);
- register/BACKLOG/CONSTRAINTS/STATE/live ledger only at closeout.

## Shared read-only paths

- Exact live source, E4 runtime, simulator/map generator, and six frozen opponents.
- D36, D82–D84, Phase 11, Phase 16, B3.1, N4, S3, mechanics, and archive index.

## Do not touch

- Resident/dev/submission sources, existing analyzers/results, raw games, bulk roots,
  fresh/official/sealed/confirmation ranges, cron, peer-owned paths, or Arena.
- No solver, candidate, policy instrumentation, selector, action restriction relabeled
  exact, endgame-switch retune, or latency budget relaxation.

## Acceptance

- Exact structural classification plus complete reused-root branching census.
- Jobs parity, focused tests, compact result/report, and sacred-source verification.
- One scope verdict with no implementation or Arena implication.
