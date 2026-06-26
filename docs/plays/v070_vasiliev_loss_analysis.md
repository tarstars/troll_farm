# v0.7.0 loss analysis — vs vasil'ev (first arena test of the economic planner)

Source: `docs/plays/game_v070_vasiliev_loss.html` (IDE dump, 2026-06-26). 600
stdout frames = 300 turns x 2 players interleaved (even=us/p0, odd=vasil'ev/p1).
Confirmed `MSG v0.7.0` on our turn 1. (Final scores not present in the DOM.)

## Command-stream comparison

| | US (v0.7.0) | vasil'ev |
|---|---|---|
| trolls | **2** (ids 0,3) | **3** (ids 1,2,4) |
| TRAIN emits | **1** | 6 (5 early + 1) |
| first extra troll | turn **73** | turn 6 |
| our train spec | `(1,3,0,2)` chopper | `(1,1,2,2)` cheap chopper |
| MOVE | 413 | 568 |
| HARVEST | 29 | 26 |
| CHOP | **48** | 15 |
| DROP | 38 | 30 |
| WAIT | 0 | 117 |

## What happened

- vasil'ev trained a CHEAP chopper `(1,1,2,2)` on turn ~5 (cc=1 -> LEMON cost only
  n+1) and reached 3 trolls.
- v0.7.0's planner chose an EXPENSIVE chopper `(1,3,0,2)` (cc=3 -> LEMON cost n+9 =
  10 at n=1). It took until turn 73 to afford it, then never expanded again -> 2
  trolls. We actually out-chopped them (48 vs 15) but still lost.

## Root cause (confirmed in the sim)

On `generate_bronze` maps the planner's first pick is `(1,3,0,2)` on 6/10 seeds
(else the `(2,2,2,0)` gatherer), averaging **2.3 trolls**; on some maps it never
affords its first investment at all -> **1 troll**. So the planner is stuck at the
same ~2-troll ceiling the greedy bot had, and its expensive first pick trains late
or not at all.

Two contributing issues:
1. **Menu gap:** `CHOPPER_SPECS` are all cc>=3 (`(1,3,0,2),(2,4,0,3),(2,4,0,4)`) —
   there is no cheap early chopper like vasil'ev's `(1,1,2,2)`. The planner cannot
   choose the fast/cheap expansion that won.
2. **Structural expansion cap, not supply scarcity:** scaling `fruit_supply` x3 in
   the sim did NOT change troll count (2.75 either way) — uniform scaling preserves
   the argmax. The planner caps at ~2-3 trolls because of the cost/benefit STRUCTURE
   (training cost `n+stat^2` vs the marginal gathering value over the finite
   horizon, with the per-type supply cap giving diminishing returns), not because
   supply is too low.

## The deeper limitation

The model is **single-agent**: it maximises OUR economy in isolation. vasil'ev won
with 3 trolls despite lower harvest (26 vs 29), lower chop (15 vs 48), and 117 idle
WAITs — i.e. the 3rd troll's value was largely COMPETITIVE (board presence /
contesting / denial), which a single-agent economic model structurally cannot see.
So the planner will keep choosing the "economically optimal" 2-troll line even when
out-expanding the opponent would win.

## Candidate fixes

- (A) **Cheaper spec menu** — add a cheap chopper (e.g. `(1,1,0,2)`/`(1,1,2,2)`) and
  cheaper gatherers so the planner can train early and expand. Low-risk tempo gain;
  but the projector may still rank the expensive line higher (needs check).
- (B) **Projector valuation** — investigate why expansion caps at 2-3 (ramp delay,
  cost handling, supply-cap diminishing returns) and whether it over-penalises a
  3rd/4th troll.
- (C) **Opponent-awareness** — give the model a reason to match/exceed the
  opponent's troll count (the competitive value the single-agent model misses).
  Biggest change; addresses the structural limitation directly.
