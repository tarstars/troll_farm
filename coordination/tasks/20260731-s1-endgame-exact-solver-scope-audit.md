# 20260731-s1-endgame-exact-solver-scope-audit

- Status: done — `FULL_EXACT_INFEASIBLE`; peer review pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER S1 / endgame exact solver
- Base commit: 8dc2f9d13b13c8cf8ccbb20d3964ac2539ee5288
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T00:13:34Z
- Last updated UTC: 2026-07-31T00:38:03Z

## Progress

- Claim/protocol published at `c980127c3817baee2f562f4efb1015983c418afc`.
- Analyzer/test hashes:
  `a1bc3175ddbae9b0628c970b318446d16ee484cbc37d0b889f8b6a1b7bdaf3cb` /
  `2acb4ec93e8a19b3ae3f5abb15f4b03b814c62b561b200924dc6d75bf53cbbd0`.
- Six focused tests and self-test pass.
- Exact movement resolver matches the engine on collision/swap/stay/speed fixtures.
- Seed 0/motion reaches turn 251 with 440 movement-only joint outcomes.
- Implementation lock:
  `local_codex_1/s1-endgame-solver-feasibility/implementation-lock.json`.
- Jobs-8 completes 720/720 games and 589 roots. Reach is 246/720 at t251, 188/720
  at t276, and 155/720 at t291. Movement-only joint outcomes: median 600, max 6,400.
- Provisional `FULL_EXACT_INFEASIBLE`; jobs-1 parity pending.
- Jobs-1 phase marker: 240/720 games complete without an integrity exception.
- Jobs-1 completes and matches jobs-8 in normalized payload, game rows, and root rows.
- Final `FULL_EXACT_INFEASIBLE`: first-ply branching is not the sole rejection; full
  remaining-horizon simultaneous exactness fails the current state/runtime object.
- Report:
  `data/analysis/live-agent-6553250/s1-endgame-solver-feasibility-result-2026-07-31.md`.
- Manifest:
  `local_codex_1/s1-endgame-solver-feasibility/manifest.json`.
- N4 and S3 remain unchanged; no solver, source, candidate, or Arena action exists.

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
