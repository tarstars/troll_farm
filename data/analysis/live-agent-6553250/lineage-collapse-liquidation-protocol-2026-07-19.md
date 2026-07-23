# Lineage-collapse liquidation — frozen protocol, 2026-07-19

## Hypothesis

The exact resident creates a material post-turn-100 state in which adaptive Gold has no banked or
carried BANANA, no banana fruit on its own crops, and no surviving opponent-owned BANANA crop. If
that boundary is causally valuable, a one-way switch from the resident's renewable scheduler to a
complete liquidation scheduler should prevent external rebootstrap, convert the remaining board
to banked wood, and improve terminal margin. Continuing the orchard may instead be necessary; the
experiment distinguishes those explanations.

## Frozen controller

Base policy is the byte-equivalent exact resident `SecureOrchardBot`. Maintain causal plant
provenance from observed births and our own PLANT attempts. An initial plant is natural. A new plant
at a cell attempted by us on the preceding turn is ours; any other unambiguous new plant is the
opponent's.

The switch is eligible only when all of the following hold in the pre-command state:

- turn is greater than 100;
- at least one opponent-owned BANANA crop has previously been observed;
- opponent banked BANANA is zero;
- sum of BANANA carried by opponent workers is zero;
- fruit on all surviving opponent-owned BANANA crops is zero; and
- no opponent-owned BANANA crop survives.

On the first eligible turn, enter liquidation permanently. Do not add a score, turn, map, seat,
duration, or opponent-identity filter.

In liquidation:

1. A loaded worker returns to a walkable cell adjacent to its shack and drops there.
2. Empty workers are coordinated against plants. BANANA plants sort before every other species;
   within a species, ripe fruit sorts first, then lower health, then path distance, then cell.
3. Assign each worker in ascending ID order to the best still-unassigned reachable plant. If fewer
   plants than workers remain, surplus workers join the first assigned target so capacity is not
   idle.
4. A worker at its target issues CHOP; otherwise it MOVEs to the target cell.
5. No TRAIN, PLANT, PICK, HARVEST, or MINE command is issued after entry.

These rules are fixed before candidate outcomes. No alternative ordering or entry state may be
selected from the result.

## Profiles and panels

Every cell contains three profiles:

- exact resident;
- exact adaptive-density farm as a context baseline; and
- lineage-collapse liquidation candidate.

Integrity uses consumed seeds 0--29, both seats, exact adaptive Gold, 180 rows, and a byte-identical
repeat with 20 workers. Discovery uses fresh seeds 2140--2199, both seats, all eight fixed local
opponents. If and only if discovery passes, run sealed confirmation seeds 2200--2259 once.

## Required telemetry and integrity

Record switch turns, first switch, prior opponent BANANA crops seen, base-command mismatches before
entry, entry stock, entry scores and margin, liquidation command verbs, opponent BANANA recovery,
and plants/banana plants remaining at terminal.

Require:

- complete seed/seat/opponent/profile grids and all games complete;
- byte-identical integrity repeat;
- zero resident-shadow mismatches before entry;
- zero switches before turn 101, without a previously observed opponent banana crop, or outside
  the exact frozen lineage-absence state;
- persistent liquidation after entry and zero forbidden post-entry verbs; and
- at least 95% wood provenance assignment, with crop ownership derived only from observed births
  and our preceding PLANT attempts.

Any integrity failure rejects the implementation rather than the hypothesis.

## Frozen discovery gate

All comparisons are paired candidate minus exact resident on identical cells. Discovery passes
only if all are true:

- overall mean margin delta at least +3.0;
- 10% trimmed mean margin delta nonnegative;
- positive mean margin delta on at least five of eight opponents;
- worst opponent-family mean margin delta no worse than -12.0;
- adaptive-Gold mean margin delta at least +5.0;
- adaptive-Gold opponent score decreases by at least 5.0 without candidate own score decreasing
  by more than 10.0; and
- at least 30/120 adaptive-Gold cells switch, so the causal test has breadth.

If discovery fails, seeds 2200--2259 remain sealed and the liquidation interpretation closes
without threshold or target-order tuning.

## Frozen confirmation and transfer rule

Confirmation must independently satisfy the same directional gates, with overall mean margin
delta at least +2.0, trimmed mean nonnegative, at least five positive opponent families, worst
family no worse than -12.0, adaptive-Gold margin at least +3.0, and at least 25 adaptive switches.

Passing local confirmation authorizes source integration and the existing arena-transfer gate; it
does not authorize automatic submission. Arena mutation still requires an exact source/hash audit
and explicit user authorization.
