# Total Map Value Ownership — design

**Goal / success gate:** create a diagnostic-backed strategy layer that maximizes our captured
share of total remaining map value, then use it to choose a narrow arena candidate. The first
candidate should not ship until the diagnostic shows a repeatable ownership leak in losses.
Arena promotion/revert still follows `docs/arena-queue.md` policy v2.

**Context:** recent rejected candidates exposed the same strategic failure from different angles:
we can make the map or our farm richer, but live opponents often convert that added value better
than we do. This is the "pie logic" problem. The correct objective is not raw production, raw
farm size, or raw tree preservation. The objective is the amount of total remaining map value
that becomes ours, plus the value denied from the opponent when they would otherwise capture it.

## Shape: ownership model first, farm governor second

This feature has two layers:

- **Global ownership model:** classify total remaining map value by projected owner.
- **Pressure-aware farm governor:** apply the model to our local farm first, because planted
  farm trees are value we create and therefore the easiest value to accidentally donate.

Do not start with a global planner rewrite. The first implementation should be diagnostic-only.
The first behavior candidate, if diagnostics justify it, should be a narrow farm-control
candidate such as `v1.53.0-pressurefarm`.

## Global invariant

For the current map state, choose actions that increase our expected captured share of total
remaining map value, after accounting for:

- travel time;
- action time;
- banking time before turn 300;
- worker capacity and role fit;
- opponent ETA and worker strength;
- future fruit/seed value;
- opportunity cost of planting, preserving, harvesting, defending, contesting, or liquidating.

The target is:

> maximize resources that become ours, or deny resources that would otherwise become theirs.

The target is not:

> maximize resources that exist on the map.

## Ownership buckets

For each relevant value source, estimate one bucket:

- **Ours:** our worker can capture it with enough margin.
- **Opponent's:** opponent can capture it first or contest it profitably.
- **Uncertain:** both sides can plausibly capture it; preserving or creating more of it may
  feed the stronger converter.
- **Dead:** unlikely to be collected or banked by either side before the game ends, or too
  expensive to collect.

The first model should be deliberately rough. A BFS/ETA estimate is enough to expose whether
losses share a structural ownership leak.

## Value sources

Count these separately because they imply different actions:

- **Banked inventory:** already captured.
- **Carried inventory:** ours only if bankable before endgame.
- **Ripe fruit:** immediate score plus possible seed value.
- **Trees:** wood value plus possible future fruit/seed value.
- **Planted farm trees:** created value; good only while likely owned by us.
- **Seed reserve:** future farm continuity, but a liability if opponent can capture it first.
- **Native/neutral trees:** shared value; useful only if our ETA/payoff beats local production.
- **Opponent-side factory trees:** possible raid targets only under strict payoff and ETA limits.

## Diagnostic design

Add a diagnostic over DEBUG/raw games before changing behavior.

Required output at phase cuts t75, t150, t225, and final:

```text
t=150 total=180 ours=72 opp=55 uncertain=41 dead=12 created_exposed=18
t=225 total=92 ours=31 opp=46 uncertain=10 dead=5 created_exposed=27
```

Minimum fields:

- total remaining value;
- projected ours;
- projected opponent;
- uncertain;
- dead;
- created/exposed value: value from our planted farm that is not safely ours;
- own-half exposed value;
- opponent late capture from values previously marked uncertain/opponent-owned.

Recommended implementation:

- compute the ownership model in Rust from live per-turn `State`, where current trees, workers,
  inventories, shacks, and walkable cells are exact;
- emit `@TFOWNCFG` and `@TFOWN` rows from DEBUG builds only;
- use BFS distances from current worker positions to tree/fruit cells;
- approximate chop/harvest turns from live troll stats;
- approximate bankability from distance to tent-adjacent cells and remaining turns;
- use optional Python only to aggregate `@TFOWN` rows into CSV/report output.

## First field questions

The diagnostic should answer these before any candidate is built:

1. Do losses show a drop in projected owned share before the score gap appears?
2. Is the leak mostly value we created, native/neutral value, or opponent factory value?
3. Does opponent late CHOP after t150 come from our half or near our farm?
4. Does exposed farm value correlate with known bad probes such as `plcc`?
5. Are `mikdiet`/`kurigen`/`Dasein8` losses explained by the same ownership leak or by a
   different production loop?

If the answer is "no repeatable ownership leak", this feature remains a strategic model and
should not become the next arena candidate.

## First behavior candidate: pressure-aware farm governor

If diagnostics confirm exposed created value, build a narrow farm governor.

Diagnostic update from `data/analysis/map-value-ownership/report.md`: the first Rust `@TFOWN`
probe did confirm the ownership-leak shape, but the strongest repeatable signal was **own-half
exposed value** in losses, not created farm exposure alone. `v1.53.0-pressurefarm` should still
start as a narrow farm governor, but its trigger should observe local/own-half pressure and only
then cap planting, release seed reserve, or liquidate exposed farm trees. Do not turn this into a
global planner rewrite.

Postponed target: AUROC-style validation of ownership scores against win/loss is useful later, but
it is not the next priority. The immediate priority is to feed the ownership score into narrow
decision making and measure whether that changes outcomes and ownership buckets in the intended
direction.

Expected behavior changes:

- dynamic farm cap: stop or reduce planting under pressure;
- dynamic seed reserve: protect seed trees only while we expect to own them;
- exposed-tree liquidation: fell farm trees earlier when opponent ETA makes preservation bad;
- optional strict late raid: target enemy/neutral factory trees only when payoff clearly beats
  defending local production.

Farm state buckets:

- **Green:** farm value is safely ours; normal behavior.
- **Yellow:** opponent power or ETA is becoming relevant; pause expansion.
- **Orange:** exposed created value exists; prioritize converting it before opponent arrival.
- **Red:** raid imminent; release seed reserve and liquidate exposed farm trees if profitable.

This must be observed-triggered. Do not implement:

- always smaller farm;
- always earlier liquidation;
- static turn-gated roam widening;
- simple seed protection or late seed-home priority;
- global planner rewrite.

Those shapes overlap with already rejected or high-risk lines.

## Code touch points

Diagnostic:

- `rust/src/botmain/ownership.rs`.
- `rust/src/botmain.rs` DEBUG emission.
- `cgauto/map_value_ownership.py` for report aggregation only.
- Fresh DEBUG raw data in `data/boss5_games/` containing `@TFOWN`.

Behavior, only after diagnostic:

- `rust/src/botmain/tactics.rs`: add pressure/ownership fields to `Plan`.
- `rust/src/botmain/planner.rs`: suppress planting, release seed reserve, or raise exposed
  fell candidates based on the pressure fields.
- `rust/src/botmain.rs`: add constants only after useful thresholds are measured.

Existing related notes:

- `docs/map-value-ownership.md`
- `docs/pressure-aware-farm.md`
- `docs/silver-experiment-log.md`
- `docs/arena-queue.md`

## Testing and gates

Diagnostic gate:

- Run against recent raw/debug games already collected for `plcc`, `mikdiet`, `kurigen`, and
  boss/local probes where available.
- Report win/loss ownership bucket averages by phase.
- Show at least one concrete replay where the ownership model predicts the later leak.

Candidate local gate:

- full Rust release test suite;
- bundle/minify/compile gates;
- equality against the intended baseline where applicable;
- boss 8 plus field probes including `plcc`, `mikdiet`, and `kurigen` or `Dasein8`;
- reject locally if our wood craters or opponent late captured value rises.

Arena gate:

- use `docs/arena-queue.md` policy v2;
- keep at `delta >= +0.5`;
- promote at `+1.0` once or `+0.5` twice;
- reject/revert at `delta <= -0.5`;
- goal remains Gold rank `<=99` verified twice.

## Risks

- **False precision:** a rough ownership model may look numeric but still miss timing details.
  Mitigation: use it first as a loss classifier, not as direct policy.
- **Pie expansion:** preserving or planting more trees may help opponents more than us.
  Mitigation: require projected ownership, not projected existence.
- **Over-liquidation:** converting the farm too early may destroy our own late production.
  Mitigation: trigger only on observed pressure and measure our wood/output in gates.
- **Opponent diversity:** some losses are fruit/scale loops, not farm raids.
  Mitigation: classify by source of captured value before choosing the behavior change.

## Exit

This spec is ready to become an implementation plan only after the diagnostic is written and
shows a repeatable ownership leak. At that point create:

- `docs/superpowers/plans/2026-07-09-total-map-value-ownership.md`

with task steps for the diagnostic, then the narrow `v1.53.0-pressurefarm` candidate if the
data supports it.
