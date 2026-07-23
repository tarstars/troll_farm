# Rich-opponent scheduler transition study — result, 2026-07-19

## Verdict

Three mechanisms replicate across the frozen 12/9 split and are eligible for v2:

1. **coordinated later funding**;
2. **hybrid-capable, genuinely multi-role workers**; and
3. **a late renewable farm/wood loop**.

The fourth hypothesis—front-loaded scale to four workers—fails in both partitions.  A universal
proxy should target three workers and continuous production, not suspend production while rushing
to four.

This is observational mechanism evidence from consumed replays.  It does not prove that copying
the scheduler improves our candidate.

## Integrity

- Exact cohort: 21 old-zoo-uncovered `rich3plus:farm_wood:train_now` games.
- Frozen split: 12 discovery, 9 confirmation.
- All 21 command streams equal their decoded state streams.
- Zero unknown replay diff updates.
- Every spawned worker matches a successful TRAIN and spec.
- All reconstructed final score/resource/action signatures exactly equal the independent field
  census.

Artifact: `rich-opponent-scheduler-transition-2026-07-19.json`.

## Replicated mechanism matrix

| Mechanism | Frozen requirement | Discovery | Confirmation | Replicates |
|---|---|---:|---:|:---:|
| Front-loaded scale | median worker 3 <=t100; >=60% games end 4+ | t69.5; 58.3% | t114; 33.3% | no |
| Coordinated later funding | >=50% later TRAINs have 2+ useful contributors | 25/26 = 96.2% | 15/15 = 100% | yes |
| Hybrid workers | >=50% trained hybrid; >=40% long-lived multi-role | 68.4%; 46.0% | 70.8%; 45.5% | yes |
| Late renewable loop | >=45% late plants/wood; both cycles in >=60% games | 78.4%; 94.5%; 100%/100% | 75.0%; 96.6%; 100%/100% | yes |

## What the scheduler actually looks like

The first worker is always bought immediately: median turn 1 in both partitions.  The third
worker is not rushed universally.  Every game eventually reaches at least three workers, but the
confirmation distribution is six games with 3 workers, two with 4, and one with 7.  That outlier
explains why the earlier rich-cluster mean looked like “four workers.”

The action stream contains two persistent hub cycles:

- **fruit/farm:** HARVEST→DROP and DROP→HARVEST dominate banking/funding, while
  HARVEST→PLANT, PLANT→HARVEST, and PICK→PLANT maintain renewable supply;
- **wood:** repeated CHOP→CHOP runs end in CHOP→DROP, followed by DROP→CHOP.

Confirmation averages per game include 58.1 HARVEST→DROP, 30.0 HARVEST→PLANT, 29.2
PLANT→HARVEST, 36.0 CHOP→DROP, and 35.1 DROP→CHOP transitions.  Thus “coordinated funding” does
not mean all workers abandon production to chase a TRAIN cost.  Multiple productive workers bank
useful resources over a long window while their ordinary farm/wood cycles continue.

The phase shift is equally stable.  Mean CHOP commands rise from about 3 in turns 1--50 to 17--21
in 101--150 and 46--48 in 251--300.  PLANT also rises late, reaching 13--14 per game in 201--250.
Harvest remains roughly 16--21 per 50-turn phase.  The farm is not an early setup discarded for
liquidation; it keeps renewing while wood throughput accelerates.

## Why v1 failed

v1 entered a global “funding mode” whenever worker three/four was unaffordable.  That displaced
the exact productive cycles that fund later workers in the replays.  It also forced four workers,
while most held-out rich games stop at three, and gave its later worker another generalist spec
instead of the common producer-producer-chopper structure.

## v2 design constraint

Use two continuous producer/funders followed by one chopper.  The producers keep harvesting,
banking, picking, and planting while their drops accumulate the third-worker cost; they may split
deficit-biased targets but never enter an exclusive funding state.  Stop at three workers.  Cross
only replay-supported immediate producer specs, cheap versus strong third-chopper specs, and a
late hybrid-role switch.  Everything else stays fixed.
