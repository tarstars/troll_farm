# Persistent-planner distillation feasibility

## Decision

Do **not** build a shallow feature-rule wrapper from the persistent planner. The frozen command
changes are too sparse, too spatially specific, and not separable across whole-game validation
folds. This route fails offline before Rust generation, adaptive panels, or platform use.

Claude implemented the first analyzer under a USD3.25 cap; the call reached its cap after writing
the code, tests and evidence but before a final narrative. Primary reviewed the implementation,
added strict fresh dated-output guards and a searched-turn-only control, and reran the analysis.
Focused suite: **22 passed in 12.02 seconds**.

## Frozen join and taxonomy

The analyzer hash-guards exact V439, the mature 160-game archive, the combined planner source and
its 160-stream report. It fail-closes on game order, agent seat, decoded turn count, packaging-arm
commands, changed-turn indices, timing counters and source totals. The joined data contain 43,263
observed turns, 9,635 searched turns, 388 changed roots and zero fallbacks.

The planner command line differs from V439 on 422 turns in 101 games. Of these, 388 are direct
root changes and 34 are later persistent-memory divergences. Every difference is turn 220 or later
with exactly two commands on each side. Dominant transitions are MOVE->MOVE 138, CHOP->MOVE 95,
command removal to WAIT/absence 105 combined, CHOP->HARVEST 32, PLANT->DROP 29, DROP->MOVE 24 and
MOVE->CHOP 22.

Only 137/422 changes admit even an optimistic target-free command rewrite. The other 285 require a
new spatial target, so a trigger alone cannot reproduce them without reintroducing planner-like
selection work.

## Leakage-safe trigger result

Five deterministic folds keep each entire physical map/game together. The shallow integer trees
use only current GameState aggregates and V439's proposed verb counts—no ids, seeds, outcomes,
future state, opponent source, or planner fields.

On the full data, each fold's best precision at at least 70% recall is only **2.58% to 6.00%**;
false-positive rates on unchanged turns are **18.89% to 22.85%**. Even the best-precision points
reach only 4.84% to 11.22% precision (with low recall). This is nowhere near the frozen gates of
90% precision, 70% recall, and at most 0.1% false positives.

Primary also gave the learner the stronger searched-only control, removing every known-ineligible
pre-turn-220 example. At at least 70% recall its precision remains **4.14% to 5.46%**, with
58.15% to 99.68% false positives. One fold finds a 66.67%-precision three-turn niche, but recall is
only 1.96%; other folds do not reproduce it. Optimistic exact-command emittability is also far below
the required 90%.

Exact evidence:
`/data/separate_troll_farm-working/planning/2026-09-05/planner-distillation-v2/`.
Report SHA `6d8234f870a3ea53ecc6304c51d30de0057e8ff2668dcb91ff5d9e20f3910988`;
taxonomy SHA `c481cbea9b9e4dd1cb9e8423842d4ce2f0c54aa3e53a0f9a5c4771fc72261247`;
analyzer SHA `9e0a5862ca4bf3e7adcfb98351c17d03dcce7df03ff71753a2984cb0203a08b2`;
test SHA `dbe5edcf2747a9f8bb63679908801d8db3415e684db3b9fa455bd20c2a40ad2b`.

This is on-policy observed-state imitation and cannot prove gain even if fidelity were high. Since
fidelity is decisively low, no candidate source was emitted. Live V439, canonical sources, the
platform, and the read-only neighbor remain unchanged. A future cheap planner must preserve the
spatial action-generation mechanism itself in a much smaller specialized implementation; aggregate
feature distillation is closed.
