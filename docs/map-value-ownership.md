# Total Map Value Ownership

Canonical Superpowers spec:
`docs/superpowers/specs/2026-07-09-total-map-value-ownership-design.md`.
Diagnostic plan:
`docs/superpowers/plans/2026-07-09-total-map-value-ownership.md`.

## Feature Request

Optimize for our captured share of **total remaining map value**, not for raw production and
not for local farm size.

The bot should treat every resource-producing object as a potentially shared asset: existing
trees, future tree growth, fruit on trees, carried resources, banked tent stock that can become
seeds, and planted farm trees. Creating or preserving value is only good when we expect to
capture enough of that value before the opponent does.

This is the general version of the "pie logic" concern: if we make the map richer but the
opponent converts the extra value better, the change is bad even when our local score or wood
count improves in isolation.

## Global Invariant

For the current map state, choose actions that increase our expected captured share of total
remaining map value, after accounting for:

- travel time;
- action time;
- banking time before turn 300;
- ownership race against opponent workers;
- future fruit/seed value;
- opportunity cost of defending, harvesting, planting, or liquidating.

The target is not "maximize resources on the map". The target is "maximize resources that become
ours, or deny resources that would otherwise become theirs".

## Ownership Buckets

For each relevant map value source, estimate one of these states:

- **Ours:** our worker can capture it with good margin.
- **Opponent's:** opponent can capture it first or profitably contest it.
- **Uncertain:** both sides can plausibly reach/capture it.
- **Dead value:** likely unreachable, unbankable before game end, or too expensive to collect.

This does not need a perfect simulator at first. A simple BFS/ETA model is enough for a
diagnostic pass:

- nearest suitable worker ETA;
- harvest/chop action count;
- carrying capacity and likely bank trip;
- opponent ETA and chop/harvest capability;
- remaining turns.

## Value Types

The first model should score value coarsely:

- banked inventory: already captured;
- carried inventory: captured only if bankable before endgame;
- ripe fruit: immediate fruit value plus seed value if it can be planted profitably;
- trees: wood value from felling plus future fruit/seed value if preserved;
- planted farm trees: created value, but exposed if opponent can capture it;
- neutral or opponent-side trees: useful only if our ETA/payoff beats normal local production.

The exact constants can be rough. The first goal is diagnostic signal, not final policy quality.

## First Diagnostic

Before changing arena behavior, add a diagnostic over DEBUG/raw games:

1. Compute ownership buckets at fixed phase cuts: t75, t150, t225, and t300.
2. Track total remaining map value, projected ours, projected opponent, uncertain, and dead.
3. Separate value we created ourselves from native/neutral value.
4. In losses, check whether opponent late score comes from value that our model had marked
   uncertain or opponent-owned earlier.
5. Compare results against field probes already used for gate decisions: `plcc`, `mikdiet`, and
   `kurigen` or `Dasein8`.

Useful output shape:

```text
t=150 total=180 ours=72 opp=55 uncertain=41 dead=12 created_exposed=18
t=225 total=92 ours=31 opp=46 uncertain=10 dead=5 created_exposed=27
```

If losses show high late opponent capture from uncertain/exposed value, this feature has a
measurable target. If not, it should remain a strategic model, not become the next candidate.

## First Concrete Application

The first behavior candidate should still be the pressure-aware farm governor:

- document: `docs/pressure-aware-farm.md`;
- likely candidate: `v1.53.0-pressurefarm`;
- reason: the local farm is value we create, so accidental donation is easiest to measure and
  easiest to control.

Do not start with a global planner rewrite. Start by measuring total map ownership, then apply
the result to a narrow farm-control decision.

## Code Touch Points

Likely diagnostic script:

- `cgauto/map_value_ownership.py` or an extension to `cgauto/battle_taxonomy.py`.

Likely behavior touch points after diagnostics:

- `rust/src/botmain/tactics.rs`: add pressure/ownership fields to `Plan`.
- `rust/src/botmain/planner.rs`: use ownership to suppress planting, release seed reserve, or
  prioritize exposed-tree liquidation.
- `rust/src/botmain.rs`: only add constants after the diagnostic establishes useful thresholds.

## Success Criteria

Diagnostic success:

- Losses should show a repeatable pattern where our expected share of total map value drops
  before the scoreboard gap appears.

Candidate success:

- Reduce opponent late captured value without reducing our own captured value enough to offset
  it.
- Pass local field probes before arena.
- Arena verdict still follows `docs/arena-queue.md` policy v2.
