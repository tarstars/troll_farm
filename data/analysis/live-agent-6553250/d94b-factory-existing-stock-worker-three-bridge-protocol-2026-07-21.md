# D94b factory existing-stock worker-three bridge — frozen protocol

Date: 2026-07-21  
Status: frozen before implementation and outcome execution

## Treatment

Start from exact D89. Preserve its resident opening, second-worker spec/timing, activation boundary,
initial BANANA budget, reserve protection, and trained wood role.

After all initial bank BANANAs have been planted and while workforce is exactly two:

- finish any already-started banana harvest/replant transaction before funding work;
- if the starter carries bill fruit, bank it;
- otherwise choose a deposited deficit among PLUM, LEMON, and APPLE by largest missing units,
  tie-breaking in that order, then harvest the reachable ripe tree of that species with greatest
  immediately bankable deficit progress, shortest travel-plus-home distance, and coordinate order;
- if no missing ripe target exists, execute unchanged D89 starter behavior;
- the trained worker banks all cargo first; while deposited IRON is below the exact bill, it moves
  to the nearest reachable mining cell, mines, and banks; otherwise it executes unchanged D89 wood
  behavior;
- append `TRAIN 2 2 0 2` only when the deposited bill is executable, the shack is clear, and more
  than 20 turns remain; and
- after worker three appears, stop all bridge logic and let unchanged D89 assign every non-starter
  worker to wood/logistics.

No bridge `PICK` or `PLANT` is allowed. BANANA factory actions may still use their existing
PICK/HARVEST/PLANT grammar. No opponent name, map identity, outcome, score, turn threshold beyond
the engine horizon, source count, deficit coefficient, target bonus, or alternate worker spec is
allowed.

## Stage A: consumed causal panel

Use maps `9,914,032--9,914,047`, both seats, all eight unchanged opponents. Run resident, exact
D89, and D94b in one deterministic harness, then repeat with one and 20 threads.

### Integrity and mechanism gates

1. Complete 768 rows / 256 triples; repeated outputs byte-identical.
2. Resident and D89 arms reproduce their pinned action/state hashes and all terminal fields.
3. Zero preactivation mismatches, illegal commands, failed affordable TRAIN attempts, bridge
   non-BANANA PLANT/PICK commands, or post-training bridge commands.
4. Exact initial BANANA bootstrap completes in at least 95% of tasks.
5. Worker three is trained in at least 128/256 tasks, across both seats and all eight families.
6. At least 95% of trained tasks record both successful bill-fruit harvest and successful IRON
   mining; worker count never exceeds three.
7. At least 192/256 tasks retain a successful post-bootstrap banana harvest/replant cycle.

### Development value gates versus D89

1. mean margin delta is positive and its map-cluster normal 95% lower bound is nonnegative;
2. mean own-score delta is at least -20 and mean opponent-score delta is nonpositive;
3. strict improvements outnumber regressions;
4. at least six opponent-family means are positive and the worst is at least -5;
5. p10 paired margin delta is at least -60 and worst is at least -160; and
6. catastrophe count and negative-margin mass do not increase.

Failure closes this exact bridge without spec, priority, or threshold tuning. Passing authorizes a
separately frozen fresh discovery block, not candidacy or platform action. Reserve maps
`9,914,096--9,914,111` for that possible discovery and `9,914,112--9,914,127` for confirmation;
neither block may be opened during Stage A.

