# PLAN — hirewood / first-hire wood investment (frozen before any measurement)

Written 2026-09-07T01:07Z (`date -u`), before a single test or panel row exists.

## Mechanism (falsifiable)

The parent (`claude_candidate_policy_flat.rs`, sha256 95ee691e…) ranks first-hire
specs with `opening_key`, whose leading component is the raw stat sum
`movement_speed + carry_capacity + chop_power`; the acquisition estimate is only
a tie-break. The referee prices those points very differently:
`training_cost(n,(ms,cc,hp,chop))` charges `n+ms²` plum, `n+cc²` lemon, `n+chop²`
iron; `score` pays 1/fruit and `WOOD_POINTS`=4/wood; `apply_chop` pays
`min(size, free capacity)` and then deletes the plant; `tick_plants` grows the
forest for free while the bill is collected.

**Change:** replace that leading component with `hire_value` — the hire's net
points: wood it can really fell, carry and bank in the turns it will actually
have (BFS from the shack door / `movement_speed` out and back,
`predict_tree(delay+travel)`, `chop_outcome`, `min(final_size, carry_capacity)`,
one drop turn, greedy fill of the remaining horizon over *distinct* plants), at
4 points, minus the bill's fruit. Iron is priced only through the delay it adds.
`strongest_affordable` re-prices at eta 0. Everything else (eta filters, hard
deadline, one decision taken in `ensure_opening` and held) is unchanged.

Prediction: the first-hire spec changes on a field-like board; the change is
toward whichever spec banks more wood net of delay and fruit — not automatically
more chop, and on a barren board toward the cheaper, faster hire.

## Comparison, budget and decision rule (frozen)

1. `rustc 1.90.0 --test` on `claude_candidate_hirewood_a_tests.rs`, which carries
   the untouched parent as `mod baseline`. All tests must pass; both arms are
   run on one referee, same board/opponent/seat.
2. Serial 16-stream bench (`benchmark_lookahead.py --games 16`, absolute rustc
   1.90, nothing else running): max decision < 50 ms and
   `packaging_different_games == 0` (readable vs compact equality) FIRST.
3. Then exactly one panel: `candidate_compare_panel` 192 pairs, seeds
   9947500..9947507, both seats, 12 opponents, `ALLOW_ANY_MAP_SEED=1`, run-local
   `CARGO_TARGET_DIR`. Baseline arrays must match run 20260906T210944Z's.
4. **Gate (both required):** whole-panel candidate W+0.5D strictly greater than
   baseline, AND zero candidate critical issues. All failed games stay in the
   denominator. Report wins/draws/losses, points, own/opponent score, margin,
   per-opponent deltas, and how many pairs the first hire actually changed.
   Anything else is PARK. No parameter sweep, no second variant, no re-tune.

Offline only: no platform action, no commit, no holdout, no agents.
