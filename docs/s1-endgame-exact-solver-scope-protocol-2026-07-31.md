# S1 endgame exact-solver scope audit — frozen protocol

Date frozen: 2026-07-31

## Question

Is “solve the last N turns exactly” a distinct, well-posed, and plausibly deployable
50 ms policy direction, or does every tractable interpretation reduce to a closed
resident-candidate/rollout interface?

This is a premise and feasibility audit. It does not implement a solver, change a policy,
consume a fresh panel, or estimate Arena value.

## Prior boundary

- B3.1 closes retuning the resident's existing score-aware endgame switch.
- D82–D84 close truncated threatened-crop MC at its representation and latency.
- Phase 11 closes online shared-state MC at 279.46 ms p95.
- Phase 16 closes primitive MOVE residual search at +0.508 and 92.852 ms p95.
- D36 closes resident-anchored repeated job overlays.
- N4 owns intertemporal selection among exact resident candidate pairs.
- S3 owns the distinct putibuzu-shaped rollout-plus-beam question.

S1 survives only as a full simultaneous endgame game solver over both players' legal
primitive actions and exact terminal semantics. A resident-candidate restriction is not
“exact” and may not be relabeled S1.

## Frozen structural audit

Classify three objects separately:

1. **Full game object:** public game state, both simultaneous command vectors, referee
   transition/RNG semantics, stall/mercy/turn-cap terminal rules, and a specified
   zero-sum objective.
2. **Known-policy continuation:** restart or clone both bot processes, including their
   internal state and entropy, after a counterfactual branch.
3. **Resident-candidate restriction:** branch only over commands exposed by the resident
   scheduler, with an unchanged opponent continuation.

For each object, record whether it is Markov from the bot-visible state, clonable,
deployable, and already covered by a closed interface.

## Frozen empirical census

Run the exact live source on reused generated Bronze seeds `0..59`, all six immutable
opponents, and both seats under E4's deterministic child runtime:

```text
60 seeds × 6 opponents × 2 seats = 720 control games
```

Capture pre-turn public states at turns 251, 276, and 291 when reached. No fresh, official,
sealed, confirmation, or Arena state is opened.

For each root report:

- remaining nominal turns and actual terminal reason/turn;
- own/opponent unit count and movement-speed vector;
- live plants, occupied cells, inventory support, and walkable cells;
- exact distinct one-turn position outcomes from movement-only command vectors for each
  player, after same-side collision resolution;
- the product of both players' movement-only outcomes, a strict lower bound on the full
  simultaneous one-ply state branching because non-MOVE verbs are omitted.

The movement enumeration may use only direct destinations within each unit's speed plus
staying put. Every such endpoint is a legal immediate MOVE result; deduplicate after exact
`apply_moves`.

## Integrity gates

1. Exact live, opponent, analyzer, runtime, and sacred-source hashes.
2. All 720 games complete with zero malformed commands or unexpected stderr.
3. Snapshot keys are unique and every captured state is exactly at its named pre-turn.
4. Movement enumeration matches hand-built collision, swap, stay, and speed fixtures.
5. One-game trace/snapshot output is exact at jobs 1 and 8.
6. Complete census aggregates and root rows are byte-identical at jobs 1 and 8.
7. Focused tests and self-test pass.

Failure returns `UNIDENTIFIABLE`.

## Feasibility classification

- `DISTINCT_FEASIBLE` requires a full-game object that is Markov from information available
  to the live bot, exact transition and opponent branching without process cloning, a
  non-duplicated action surface, and empirical one-ply branching compatible with a
  remaining-horizon exact search under 50 ms.
- `RESTRICTED_DUPLICATE` if the only tractable object restricts to resident candidates,
  known unchanged opponent continuations, or batch overlays already owned by N4/D36/S3.
- `FULL_EXACT_INFEASIBLE` if the full object is well-defined but its necessary state,
  simultaneous branching, or runtime requirement rejects a bounded exact implementation.
- `PREMISE_UNIDENTIFIABLE` if “exact” depends on unavailable referee/opponent state or an
  unspecified opponent/objective model.

No classification authorizes an implementation. A positive classification permits only
peer review and a separately frozen solver protocol.

## Planned artifacts

- `cgauto/s1_endgame_solver_feasibility.py`;
- `tests/test_s1_endgame_solver_feasibility.py`;
- compact result/report under `data/analysis/live-agent-6553250/`;
- locks/manifest under `local_codex_1/s1-endgame-solver-feasibility/`.
