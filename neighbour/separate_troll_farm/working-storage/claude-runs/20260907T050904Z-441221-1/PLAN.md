# Frozen plan — regenerative timber in the dispatch controller (2026-09-07)

Frozen BEFORE any source change. Archive of the exact prior sources:
`archive/` (dispatch core `0990ebba`, tests `7b60e160`, `_a.rs` `5af6d9c5`).

## Mechanism (one candidate, no variants)

A complete finite **timber job**: PICK a fruit seed out of the bank (1 banked
point spent), carry it, PLANT it on a claimed plot, let the referee's real
growth law raise it to a chosen size, CHOP it, DROP the wood. Wood scores
`WOOD_POINTS = 4`; a size-1 banana is health `2 + 1*1 = 3`, so a real 1/1/1/1 or
1/1/0/1 starter nets `4 - 1 = +3` from a single seed. `apply_plant`/`apply_pick`
have no harvest-power condition, so hp0 foresters may run it; only HARVEST is
denied to them.

Priced terms: seed withdrawal (1 banked point), travel to the door, PICK, travel
to the plot, PLANT, `1 + (target-1)*effective_cooldown` growth turns,
`ceil(base + slope*target / chop_power)` felling turns, delivered wood capped by
`carry_capacity`, and the walk back plus DROP. Choice of kind and target size is
a **predeclared** enumeration of the referee's own space
(`{Plum, Lemon, Apple, Banana} x size {1,2,3,4}`), not a coefficient tuned on the
eight development maps.

Growth is not idle waiting: `Job` gains `busy` (worker-turns) separate from
`turns` (elapsed, used for the finite horizon). Density is `value / busy`, so a
planted crop is serviced by other work while it ripens.

Continuation/ownership: `DispatchBot.groves` records `(cell, kind, target,
owner, turn)` at PLANT emission and is reconciled against the board each turn.
While a unit carries a seed for its own timber project the controller offers it
**only** that project, so the seed cannot be banked away or re-aimed. A grove's
plant is invisible to every other worker, and invisible to its owner until
`size >= target`, so immature trees are not destroyed before the priced return.
Seeds are spent against a per-turn budget net of the TRAIN bill reservation, so
two workers cannot spend one seed, and the plot is an exclusive `claim()`.

## Comparison, baseline and decision rule

One candidate. Baseline: policy-flat parent `95ee691e`. 192 known development
pairs, seeds 9947500..9947507, the 12 existing adaptive opponents, both seats,
`ALLOW_ANY_MAP_SEED=1`; all 192 baseline command arrays verified against
`gap20260906T210944Z-3184968-1`. Full referee, all issue classes.

**Decision:** positive whole-panel W+0.5D versus the parent AND 0 candidate
issues supports further evaluation. Anything else -> report evidence or park.
The prior dispatch 139 points is descriptive only. No fresh maps, no favourable
subset, no post-panel tuning.

## Prerequisites, all required before the panel

1. Focused behavioural fixtures pass (real referee, actual 1/1/1/1 and 1/1/0/1).
2. Exact compact export <= 100,000 UTF-16.
3. ORIGINAL readable == pruned == compact on the 16 archived official streams.
4. Per-turn max < 50 ms, measured with no compile or panel running, with a
   corrected `exact_stream_latency.py` (EOF/empty/exit/stderr rejection,
   bounded per-read timeout, timer started before the input flush).
If any prerequisite fails, the panel is NOT run.
