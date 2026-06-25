# Economic Planner Design

**Goal:** Replace hand-tuned greedy economic heuristics with an explicit
*analytic economic model* that solves the invest-vs-bank tradeoff (how much to
sink into trolls / a strong chopper, and when) by projecting candidate build
orders to turn 300 and picking the best — re-planned every turn from the real
state. The existing reactive layer keeps doing spatial execution.

**Why:** Greedy tuning is exhausted. Five self-play sweeps (~15 variants) failed
to beat v0.6.1, yet v0.6.1 loses on the ladder, and self-play has demonstrably
diverged from the arena (see `docs/plays/v061_loss_analysis.md`). The real losses
are economic: stuck at 2 trolls because we never hold PLUM+LEMON+APPLE+IRON at
once (a per-type supply problem the greedy code is blind to), and ~70 troll-turns
wasted on a planting churn. An explicit model makes the tradeoff *solvable and
explainable* instead of leaning on a noisy proxy, and a per-type supply model is
exactly what exposes the PLUM-starvation.

**Tech Stack:** Python 3.11, stdlib only at runtime (single-file CodinGame
submission), pytest + the existing `sim/` harness for dev/validation.

## Global Constraints

- **Single-file submission.** All in-game code lives in `bot/main.py`. The
  planner is added there as pure module-level functions; `sim/` stays dev-only.
- **Runtime budget.** CodinGame turn limit ~50 ms. The projector must be O(300 x
  small) and the per-turn search a few dozen projections — microseconds total.
- **No new runtime dependencies.** stdlib only in `bot/main.py`.
- **Backward-compatible executor.** The reactive `decide()` machinery
  (pathing, banking, move-deconfliction) is reused; only its economic choices
  (what to gather, whether to plant, which TRAIN spec) become planner-driven.
- **v1 is single-agent.** The economic model ignores the opponent contesting or
  chopping our trees. Opponent interaction is handled (later) in the spatial
  layer, not smeared into the rates.

---

## Architecture

```
  observed State (real game, each turn)
        |
   [rate estimator]   measures per-map economic rates from State
        |  -> per-type fruit supply, gatherer throughput, chopper wood/iron rate
   [economic projector]   tiny rate-based forward sim (NO positions) to turn 300
        |  -> predicted score@300 for a given (state, policy)
   [policy search]   enumerate build orders, project each, pick best end-score
        |  -> next macro action + gather/plant guidance
   [reactive executor]   existing decide(); economic choices now plan-driven
        v
     commands
```

Three new pure components in `bot/main.py`, plus a thin integration in `decide()`.

---

## Component 1: Rate estimator

`estimate_rates(state) -> Rates` — pure function of the observed `State`.
Computed (cheaply) each re-plan so it tracks the real, current map.

**Outputs (`Rates`):**
- `fruit_supply[type]` for type in {PLUM, LEMON, APPLE, BANANA}: steady-state
  fruits/turn obtainable, = sum over reachable trees of that type of their mature
  production rate `1 / cooldown(type, water)` (water-adjusted via the known
  WATER_BOOST). Caps how fast each *training* resource can be collected — the
  quantity the greedy code never saw.
- `iron_supply`: iron/turn available = (reachable iron cells > 0) ? a per-miner
  rate `chop_power` per mine-action amortized over travel : 0.
- `gatherer_rate(stats)`: fruits/turn one gatherer banks ~=
  `carry_capacity / round_trip_cycle`, where `round_trip_cycle ~= 2 * mean
  reachable-tree distance / movement_speed + handling`. Capped by total
  `fruit_supply` shared across active gatherers (diminishing returns).
- `chopper_rate(chop_power, carry)`: wood/turn ~= `wood_per_tree /
  (fell_time + travel + bank_time)`, `fell_time = ceil(tree_health/chop_power)`,
  `wood_per_tree ~= mean reachable tree size` (capped by carry per trip).
- Helper distances reuse the existing `bfs_distances` from the shack.

**Notes / approximations (deliberate):**
- Distances collapse to a single mean round-trip term per role; we do not model
  which specific tree a troll visits.
- Diminishing returns modeled by capping aggregate per-type collection at
  `fruit_supply[type]` regardless of gatherer count.

---

## Component 2: Economic projector

`project(state, policy, rates) -> float` (predicted score@300). Pure, no
positions, ~300 cheap iterations.

**Abstract economic state advanced per turn:**
- `t` (current..300)
- `roster`: list of trolls as `(role, stats)`; role in {GATHERER, CHOPPER}
- `banked`: 6-vector [PLUM, LEMON, APPLE, BANANA, IRON, WOOD]
- `pending`: trolls trained but still ramping (spawned at shack, not yet
  producing) with a `ready_at` turn = `t + ramp_delay` (~mean shack->tree dist).

**Per-turn transition:**
1. Promote any `pending` troll whose `ready_at == t` into `roster`.
2. Add production to `banked`: for each fruit type, add
   `min(fruit_supply[type], sum of gatherer_rate over gatherers assigned to that
   type)`; add `chopper_rate` wood and `iron_supply` iron from choppers/miners.
   Gather assignment: a target mix that funds the next planned investment first,
   else spread to maximize bankable score (BANANA/extra -> score).
3. If the policy's next investment is due (earliest turn it becomes affordable)
   and `banked >= cost(spec, n)`: subtract the cost bundle, append the troll to
   `pending` with `ready_at = t + ramp_delay`. `cost` reuses `training_cost`.
4. End: `score = sum(banked fruit) + 4 * banked[WOOD]`. (Carried-but-unbanked is
   ignored in v1; an end-game flush is future work.)

**Key property:** because the horizon is finite, an investment late in the game
shows little/no payback and the projector ranks "just bank" above it — the
over-investment guard falls out of the model, not a tuned constant.

---

## Component 3: Policy search

`search_policy(state) -> Plan`. Run every turn (receding horizon).

**Policy = an ordered build list** of investments, each
`(role, stats)` drawn from a short menu, e.g.:
- gatherer specs: `(ms,cc,hp,chop)` like `(1,1,1,0)`, `(1,2,1,0)`, `(2,2,2,0)`
- chopper specs by power: `(1,3,0,2)`, `(2,4,0,3)`, `(2,4,0,4)`

**Timing is solved, not searched:** each investment fires at the earliest turn it
becomes affordable (choosing a strong chopper in the order already implies
banking until it is affordable — that is how "accumulate for a strong chopper"
is expressed). The planner never deliberately delays an *affordable* investment.

**Search:** enumerate a bounded candidate set of build orders (length 0..3 over
the spec menu; a few dozen), `project()` each from the current state, keep the
max. Ties broken toward fewer/cheaper investments.

**Output `Plan` (consumed by the executor):**
- `train`: the spec to TRAIN this turn if its investment is due & affordable,
  else `None`.
- `gather_types`: ordered fruit types the executor should prioritize (the
  resources the next planned investment still needs). Empty -> gather for score.
- `plant`: `(type)` to plant if the plan wants supply, else `None`.
- `chopper_spec`: the chosen chopper spec (for the executor's chopper logic).

**Receding horizon:** re-planning each turn from the *observed* state means rate
mis-estimates self-correct instead of compounding; only the next macro action is
ever committed.

---

## Component 4: Executor integration

`decide(state, params)` calls `search_policy(state)` once, then runs the existing
reactive layer parameterized by the `Plan`:
- `best_tree` biases toward `plan.gather_types` when funding an investment
  (fixes PLUM/APPLE starvation); falls back to the current round-trip key for
  score-gathering.
- Planting obeys `plan.plant` (plant only when the plan asks, of the asked type)
  — replaces the always-on orchard footprint, killing the churn.
- The chopper uses `plan.chopper_spec`; chop targeting/pathing unchanged.
- TRAIN emitted from `plan.train` (replaces `training_command`'s spec logic).

Pathing, move-deconfliction, banking, and the chopper's mine/chop/bank cycle are
unchanged.

---

## Validation & Testing

The fidelity gate matters more than any single feature, because the sim is known
to diverge from the arena.

1. **Projector-vs-sim rank correlation (GO/NO-GO).** For a set of policies on
   several `generate_bronze` maps, the projector's predicted score@300 must
   *order* the policies the same as the full `sim/` does (Spearman rank
   correlation over policies, averaged across seeds, above an agreed threshold
   e.g. >= 0.7). The search only needs correct ordering, not exact scores. If
   this fails, the model is wrong — fix it before trusting the planner.
2. **Rate estimator unit tests** on hand-built `from_ascii` maps: known trees and
   distances -> asserted `fruit_supply`, `gatherer_rate`, `chopper_rate`.
3. **Projector unit tests:** monotonicity (more gatherers -> >= score up to the
   supply cap; a late investment -> <= "just bank"); affordability respected.
4. **Planner regression tests:**
   - No reachable PLUM -> plan contains no movement-stat (ms>1) trainings (the
     exact bug that capped us at 2 trolls).
   - Rich map -> plan expands beyond 2 trolls.
   - Late game (few turns left) -> plan stops investing.
5. **Arena A/B** is the final judge: ship as a new version, test on the ladder.

---

## Decisions & Simplifications (YAGNI)

- Single-agent economic model (no opponent term) in v1.
- Distances collapse to mean round-trip per role (no per-tree routing in the
  model — the executor still routes for real).
- Earliest-affordable timing (no deliberate-delay search).
- Carried-but-unbanked resources ignored at turn 300 (end-game flush deferred).
- Chopper denial heuristic ("work near enemy camp") kept as-is in the executor;
  the model just sizes the chopper.

## Future Work (not in v1)

- Opponent interference term (expected tree loss; plant safety).
- End-game banking flush in the projector and executor.
- Tabular DP if the candidate-enumeration search ever becomes a bottleneck (the
  projector is already the transition function).
