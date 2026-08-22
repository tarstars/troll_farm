# Resident denial-scoring audit — 2026-08-07

Read-only source audit. No bot change, no corpus access, no host run, no Arena action.

**Question (owner, 2026-08-07):** does the resident "choose one of lemon or plum and
concentrate on chopping it out"?

**Answer: partly — and the concentration is carried almost entirely by the starter troll.**

- Source: `rust/src/bin/yamo_orchard_live.rs`, SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` (byte-sacred, unmodified).
- Reproduce: `python3 cgauto/analyze_resident_denial_scoring.py [--json]`
- Guard: `tests/test_analyze_resident_denial_scoring.py` (9 tests) re-reads every constant
  out of the Rust on each run and fails if the model drifts from the source.

## What the code actually does

`MoisanBot::chop_candidates` (`yamo_orchard_live.rs:1101-1105`) scores every reachable tree:

```rust
let mut score = 1000.0 * wood as f64 / turns as f64;
if Some(plant.kind) == type_to_cut && opponent_trolls <= 2 {
    let opponent_distance = manhattan(plant.cell, view.shacks[1]);
    score += 900.0 / (1 + opponent_distance) as f64;
}
```

with `wood = final_size.min(unit.free_capacity())` and
`turns = travel + chop + return + 1`.

`focus_type` (`:749-766`) selects **one** species — whichever of LEMON/PLUM has the smaller
*summed BFS distance from our own shack* — and `ensure_focus_type` (`:743-748`) freezes it for
the game. So the species is chosen for our convenience, not for the opponent's dependence on it,
and it is never revised.

Three properties follow directly, none of which is "clear the map":

1. The denial term is an **additive bonus among candidates**, not a phase. Nothing tracks
   remaining stock and nothing completes.
2. The bonus is keyed to **proximity to the opponent shack**, not to the species population.
   Focus-species trees on our own side attract almost no bonus.
3. The bonus is **exactly zero once `opponent_trolls > 2`** (`:1066`, `:1102`).

## Measured result: an emergent division of labour

`wood` is capped by carry capacity and `chop` scales with chop power, so the base term differs
about eightfold between worker classes while the denial bonus is identical for both. Tree 6 cells
from the worker and 6 from our shack; ratio is bonus ÷ base at manhattan distance *d* from the
opponent shack.

| worker | size | turns | wood | base | d=1 | d=5 | d=10 | d=20 | d=30 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| starter (1/1/1) | 1 | 19 | 1 | 52.6 | 8.6× | 2.9× | 1.6× | 0.8× | 0.6× |
| starter | 2 | 21 | 1 | 47.6 | 9.4× | 3.1× | 1.7× | 0.9× | 0.6× |
| starter | 3 | 23 | 1 | 43.5 | 10.3× | 3.4× | 1.9× | 1.0× | 0.7× |
| starter | 4 | 25 | 1 | 40.0 | 11.2× | 3.8× | 2.0× | 1.1× | 0.7× |
| trained (3/3/3) | 1 | 7 | 1 | 142.9 | 3.1× | 1.1× | 0.6× | 0.3× | 0.2× |
| trained | 2 | 8 | 2 | 250.0 | 1.8× | 0.6× | 0.3× | 0.2× | 0.1× |
| trained | 3 | 9 | 3 | 333.3 | 1.4× | 0.5× | 0.2× | 0.1× | 0.1× |
| trained | 4 | 9 | 3 | 333.3 | 1.4× | 0.5× | 0.2× | 0.1× | 0.1× |

**Crossover distance** — the range over which the bonus outweighs pure wood efficiency:
**starter 16–21 cells; trained 1–5 cells.**

Nobody assigned these roles. They fall out of the scoring: **the starter is the denial unit and
the trained worker is the economy unit.**

The allocation is inverted relative to capability. Pulled to a size-4 focus tree near the
opponent shack, the starter spends **25 turns to deliver a single wood** (12 chop turns at chop
power 1, plus travel, plus a carry cap of 1). The trained worker would fell the same tree in 9
turns for 3 wood. The unit that is worst at chopping and carrying is the one the bonus sends on
the longest errands.

That is a live, visible mechanism for the previously measured cost of denial — `CONSTRAINTS.md`
(e): *"pre-fruit denial recovers 18.8 opponent points while forfeiting 81.5 own."*

## The give-up rule already exists

`opponent_trolls <= 2` is a scale-conditioned abort: the resident denies while the opponent is
small and stops entirely once they field a third troll. The owner's proposed rule — *"if the
enemy can sustain lemons and plums faster than we chop, give up"* — is therefore **already
implemented as a trigger**. What does not exist is a destination: when the abort fires, the bot
falls back to undifferentiated wood maximisation.

This is also the one place the resident *does* condition on opponent scale, which qualifies the
B3.1 finding that *"the resident never conditions on it"* — it conditions here, and only to
switch denial off.

## Bearing on prior closures

- **N6** swept this exact weight (450 / 900 / 1800, 512 paired tasks per arm); neither
  alternative cleared its gates. *"Keep 900; do not retry zero."* The magnitude is closed.
- **H4** (`NO_MATERIAL_DENIABLE_BILL`, strict blockable rate 0.0 over 17 catastrophes,
  12 identities) closed denial as a way to *prevent* opponent scaling: 43 of 73 individually
  mandatory bill batches are IRON, which chopping cannot touch, and of the 30 mandatory fruit
  batches exactly 1 had a resident co-located, that unit could not legally HARVEST, and none
  admitted a lethal single chop.
- Neither of those touches **what should happen after the abort fires**, which is where the
  D89a seed factory (`+79.441` mean paired margin, rejected on four value gates) becomes
  relevant.

Nothing here reopens a closed branch. The audit is descriptive.

## Corrections recorded against my own statements

Both errors were mine, made in conversation before this audit was run, and both came from
quoting a figure adjacent to the one that mattered:

1. I first said the bonus *"meaningfully reorders targets only right next to their shack."*
   That is true only for the trained worker. For the starter the bonus dominates out to ~20
   cells — most of the map.
2. Earlier the same day I described D89a as failing *"only on a safety gate."* It fails four of
   fifteen value gates; the artifact's own decision string is
   `reject_value_or_safety_keep_confirmation_sealed`.

The drift-guard test exists because of this pattern: the constants are now re-read from the
source on every run rather than recalled.
