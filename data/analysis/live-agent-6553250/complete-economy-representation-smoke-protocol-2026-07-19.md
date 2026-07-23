# Complete-economy representation smoke — frozen protocol, 2026-07-19

## Question

Can a compact closed-loop policy grammar both reproduce the exact resident and express at least
one distributed, opponent-robust complete economy that beats it on reused local data?

This is a representation discriminator, not candidate discovery.  It answers whether a terminal-
outcome search has a viable policy space before investing in a field-covering opponent suite,
larger optimization, distillation, or fresh data.

## Why this is a new direction

Closed work searched isolated first-worker commands, late workforce wrappers, fixed macro options,
teacher-state imitation, short residual actions, and provenance nudges.  This smoke instead runs
each genome from turn one through the corrected terminal/stall condition as its own stateful
economy.  Training, funding, worker roles, renewable planting, protected seed supply, felling, and
banking evolve on the state distribution created by that same genome.

## Frozen grammar

The grammar has two families:

1. `Resident`: construct the exact `SecureOrchardBot::new()` policy.  This is the safe/abstention
   genotype and must be command-identical to a direct resident instance.
2. `FarmEconomy(config)`: construct one complete parameterized Gold-style economy with fields for
   maximum workers, number and specifications of choppers, training stagger, number of planter
   workers, accumulation/hold horizon, farm tree cap, and co-fell target sharing.  Its existing
   closed-loop funding, seed reserve, planting, harvesting, chopping, and banking controller runs
   unchanged.

The fixed catalog contains 31 nonresident genomes:

- four two-worker lean genomes with first-chopper specs `1/2/0/2`, `2/2/0/2`, `2/3/0/2`, and
  `2/2/0/3`;
- eight three-worker dual-chopper genomes: stagger 20 or 60, second-chopper harvest power 0 or 1,
  and farm cap 12 or 20;
- six three-worker planter/chopper genomes: hold 0, 60, or 100 crossed with farm cap 12 or 20;
- twelve four-worker planter/two-chopper genomes: stagger 30 or 60, hold 0, 80, or 120, crossed
  with farm cap 18 or 24; and
- the existing density-adaptive complete economy.

All unspecified values are frozen: first chopper `2/2/0/2`, later chopper `2/2/hp/2`, one planter
where named, no co-fell, the existing farm radius/fell/liquidation/seed-reserve policy, and exact
referee mechanics.  Do not add catalog members after seeing outcomes.

## Data and execution

- Discovery/screen: consumed generated seeds 0--29.
- Confirmation: consumed generated seeds 30--59, opened only for at most the three unchanged
  discovery selections.
- Eight fixed deterministic opponent families, both seats: CompactGold, adaptive Gold, GoldElite,
  MyBot, PrinterBot, SchedBot, ScriptBoss, and SilverBoss.
- The independent summary unit is the seed; raw cells remain seed/seat/opponent.
- Every genome and resident use identical initial maps in a cell and run through the corrected
  stall/terminal rule.
- Run with 20 workers, the available CPU count.  Record score, margin, wood, workers, successful
  TRAIN/PLANT/HARVEST/CHOP/DROP actions, terminal turn, and command divergence.

These ranges are already consumed and can never qualify a candidate.

## Integrity gate

Before reading policy outcomes:

1. `Resident` grammar and a direct resident instance must emit identical non-MSG commands at every
   turn on all discovery resident-control streams;
2. the catalog must contain exactly 31 unique nonresident labels/configurations;
3. every discovery genome must have exactly 480 cells (30 seeds × two seats × eight opponents),
   with no duplicates or missing cells; and
4. all games must terminate under the corrected rules without panic or invalid command.

Any integrity failure stops the experiment.

## Frozen discovery selection

A genome is discovery-eligible only if all checks pass versus resident:

- mean and five-percent-trimmed cell margin delta are strictly positive;
- mean and five-percent-trimmed distribution of the 30 per-seed mean deltas are strictly positive;
- favorable cells are at least as numerous as unfavorable cells;
- at least six of eight opponent-specific mean deltas are nonnegative;
- worst opponent mean is at least -10;
- mean own-score delta and mean own-wood delta are nonnegative; and
- it changes commands in at least 80 cells, successfully trains in at least 80 cells, and
  successfully plants in at least 80 cells.

Rank eligible genomes by: more nonnegative opponents, higher worst-opponent mean, higher trimmed
seed mean, higher raw seed mean, then lexicographic label.  Confirm at most the first three.

## Frozen confirmation gate

The representation passes only if at least one unchanged selected genome clears every check on
seeds 30--59:

- mean cell margin delta >= +2 and five-percent-trimmed cell mean > 0;
- mean of per-seed mean deltas >= +2 and its five-percent-trimmed mean > 0;
- favorable cells are at least as numerous as unfavorable cells;
- at least six opponent means are nonnegative and the worst is >= -5;
- mean own-score delta and mean own-wood delta are nonnegative; and
- at least 80 changed cells, 80 successful-TRAIN cells, and 80 successful-PLANT cells.

## Stop and continuation rules

- No discovery survivor: close this farm-economy grammar; do not open seeds 30--59.
- Confirmation failure: close the grammar without tuning it on either block.
- Confirmation pass: record only that the representation is expressive enough.  It authorizes no
  candidate, fresh seed, source packaging, platform game, submission, or resident change.
- After a pass, the next required iteration is a field-covering opponent-continuation suite; local
  outcome optimization is not credible for Legend transfer until that coverage problem is solved.
