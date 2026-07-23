# Pressure-Aware Farm Governor

Parent feature request: `docs/map-value-ownership.md`. Canonical Superpowers spec:
`docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md`. This document is the
first concrete application of that broader total-map-value ownership model.

## Goal

Produce as many resources as possible while capturing a larger share of the **total remaining
map value** than the opponent. The bot should not judge progress by raw production or farm size
alone. A tree, fruit source, planted seed, or preserved neutral resource is useful only when our
bot is likely to capture enough of its value before the opponent can exploit it.

This is the strategic answer to the recurring "pie logic" failure: several past changes made
more resources exist on the map, but live opponents converted the enlarged shared value better
than we did. The feature should therefore maximize **our captured share of total map value**,
not raw map value and not raw farm value.

## Core Idea

Use a global ownership rule first, then apply it to our local farm as the first controllable
subset.

Global invariant:

- For the current map state, our actions should increase our expected captured share of total
  remaining map value, after accounting for travel, timing, banking, and opponent capture risk.

Farm-specific application:

- Maintain a lean local farm near our tent, but make its size and liquidation behavior depend
  on observed opponent pressure and projected ownership.

Strict invariant:

- The local farm can be chopped down before an enemy chopper can reach and exploit it.

Weaker and more useful invariant:

- For the current local farm, our projected captured value is greater than the opponent's
  projected captured value plus the travel/opportunity cost of defending or liquidating it.

In practice, the bot should keep growing when added value remains mostly ours, stop expanding
when ownership becomes uncertain, and liquidate or contest exposed value before the opponent can
take it. The farm is only the first place to enforce this because farm trees are value we create
ourselves and therefore the easiest value to accidentally donate.

## Pressure Estimate

Each turn, estimate opponent farm pressure from observable state:

- Opponent troll count.
- Number of opponent chop-capable trolls.
- Their movement/chop/carry strength.
- Their distance to our farm and to our half of the map.
- Recent opponent production pattern, especially late CHOP/PICK/PLANT/DROP after turn 100-150.
- Whether opponent trolls are actually crossing into our half.

This must be observed-triggered. Static time gates and unconditional roam/liquidation changes
have repeatedly failed.

## Tree Ownership Model

For each tree in or near our farm, estimate:

- Our capture time: our best worker ETA + chop/harvest time + likely bank cost.
- Opponent capture time: opponent ETA + chop/harvest time.
- Value at risk: wood value, future fruit/seed value, and whether the tree is part of the seed
  reserve.

Then classify farm state:

- **Green:** opponent cannot reach profitably; normal farm behavior.
- **Yellow:** opponent power is growing or approaching; stop expanding, preserve only strongest
  seed/value trees.
- **Orange:** exposed trees exist; prioritize early fell/liquidation of trees the opponent can
  soon contest.
- **Red:** raid imminent; disable seed protection if needed and convert farm trees into our wood
  before they become opponent value.

## Candidate Shape

Likely candidate name: `v1.53.0-pressurefarm`.

Expected behavior changes:

- Dynamic `farm_cap`: reduce or pause planting under pressure.
- Dynamic seed reserve: protect seed trees only while we expect to own them.
- Earlier farm liquidation for exposed trees, but only under observed opponent pressure.
- Optional late raid response: if opponent factory is clearly stronger, our chopper may target
  exposed enemy/neutral factory trees with strict ETA/payoff limits.

Do not implement this as "always smaller farm" or "always liquidate earlier". That would repeat
the static-control failures. The feature is valuable only if it changes behavior based on
opponent pressure and projected ownership.

## First Work Item

Before changing arena behavior, add diagnostics over DEBUG/raw games:

1. For turns after 100 and 150, compute farm exposed value.
2. Split tree value by likely owner: ours, opponent, uncertain.
3. Correlate losses with opponent late CHOP from our half or near our farm.
4. Compare against known field probes: `plcc`, `mikdiet`, and `kurigen` or `Dasein8`.

If losses correlate with high exposed value, implement the governor. If not, the idea remains a
useful model but should not become the next arena candidate.

## Current Code Touch Points

- `rust/src/botmain.rs`: static farm constants such as `GE_FARM_R`, `GE_FARM_MAX`,
  `GE_CHOP_R`, `GE_LIQ_T`, and `GE_SEED_RESERVE`.
- `rust/src/botmain/tactics.rs`: builds the `Plan`, currently with mostly static farm radius,
  cap, liquidation, and seed reserve.
- `rust/src/botmain/planner.rs`: currently uses immediate race checks and static fell/plant
  bands; this is where exposed-tree fell or plant suppression would surface.

## Success Criteria

Local diagnostics should show that the candidate reduces opponent late farm capture without
cratering our own wood output. Arena verdicts still follow `docs/arena-queue.md` policy v2:
keep at `+0.5`, promote at `+1.0` once or `+0.5` twice, reject/revert at `-0.5`.
