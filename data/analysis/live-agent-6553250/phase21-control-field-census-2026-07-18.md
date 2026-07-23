# Phase 21 same-source control field census — 2026-07-18

## Outcome

The fresh exact-resident capacity control supplies an independent 131-game field census before
its battle list is replaced.  Agent `6560240`, submission `41012256`, was rank 18/107 at 24.71
during the read.  All 131 requested results parsed and there were no fetch failures.

This is observational mechanism evidence.  It arrived after the `b100_e6` candidate and arena
thresholds were frozen, so it cannot change Phase 21 or serve as candidate acceptance evidence.

| Cohort | Games | Mean margin | Our score | Opponent score | Our wood | Opponent wood | Opponent workers |
|---|---:|---:|---:|---:|---:|---:|---:|
| All | 131 | -17.61 | 199.42 | 217.03 | 47.18 | 44.27 | 2.40 |
| Wins | 68 | +74.53 | 200.65 | 126.12 | 49.26 | 22.04 | 2.03 |
| Ordinary losses | 37 | -38.00 | 193.54 | 231.54 | 46.24 | 47.76 | 2.46 |
| Catastrophic losses | 25 | -238.76 | 207.48 | 446.24 | 43.44 | 100.00 | 3.36 |

The 25 catastrophic losses are 19.1% of games but contain **80.9% of all negative-margin mass**
and span 14 opponents.  This is a repeated field mechanism, not one bad matchup.

## Analysis by abstraction level

### Effect and score decomposition

The resident's catastrophic own score, 207.48, is slightly higher than its 200.65 winning score.
The failure is therefore not primarily inability to produce points.  Opponents explode from
126.12 in wins to 446.24 in catastrophes.  Their final wood rises from 22.04 to 100.00 while the
resident's wood falls only from 49.26 to 43.44.

Opponent-crop wood explains **63.62 of the 68.88-point opponent-wood gap** between catastrophic and
noncatastrophic games, or about 92.4%.  Catastrophic opponents collect 84.04 wood from trees they
planted; the resident collects 13.32 from those trees.

### Scheduling mechanism

Catastrophic opponents create 42.56 crops on average.  Every one is within the census's 20-turn
reach bound when born, with median resident ETA 6, yet the resident contacts only 9.40 (22.7%).
Winning games have a 64.5% interception rate.  The missing action is timely prioritization of
reachable opponent-created supply, precisely the bounded mechanism in the frozen candidate.

### Workforce and complete economy

The resident finishes every cohort with exactly two workers and one successful TRAIN.  Catastrophic
opponents average 3.36 workers, 42.68 plants, and 116.20 harvests.  Their extra workers matter as a
coupled renewable economy, not as an isolated worker-count statistic: prior forced-worker,
farm-first, funding, and handoff experiments already show that adding a worker without its role and
supply policy loses.

### Temporal dynamics

In catastrophic games the resident is still ahead at turn 100: score 72.00 versus 40.16 and wood
12.52 versus 4.60.  The opponent already averages 2.56 workers.  By turn 150 the score is close
(107.28 versus 91.96); by turn 200 the opponent leads 198.04 to 141.12.  The decisive failure is a
midgame compounding transition after an apparently healthy opening, not a turn-one deficit.

The strongest descriptive early rule is `turn-100 opponent workers >= 3` and `turn-100 opponent
harvests >= 30`: 11/17 selected games are catastrophic (64.7% precision, 44.0% recall) across 11
opponents.  This is a diagnostic cohort, not a justified live selector.

### Geometry

Catastrophic maps have much longer shack-door distance (11.96 versus 7.08, standardized difference
1.22) and more/larger private trees.  Resource abundance lets worker-rich opponents compound while
also increasing the resident's banking travel.  Door distance is a risk context, not yet a causal
intervention; earlier routing audits found no generic target-reachability defect.

### Opponent heterogeneity and statistics

The same opponent can produce both large wins and catastrophic losses: `uta_ccc` spans -547 to
+263 and `gaha` spans -521 to +226.  Identity-only tables would overfit.  Map state, workforce
transition, and crop ownership are materially more useful than opponent nickname.

## Hypotheses and priorities

1. **Current test — bounded crop interception.**  The frozen `b100_e6` candidate should reduce
   opponent compounding, catastrophic rate, and negative-margin mass without materially reducing
   resident production.  Only its controlled arena comparison can establish transfer.
2. **If Phase 21 promotes — measure the new residual.**  Repeat the effect census on a mature
   candidate stream.  Do not assume the old tail remains; attribute whatever negative mass survives
   before designing another change.
3. **If the crop component remains — test a distinct provenance-aware scheduling mechanism.**  Use
   new discovery/replication blocks and exact fallback; do not retune `b100_e6` on its arena games.
4. **If crop compounding falls but worker-rich losses remain — synthesize a complete economy
   closed-loop.**  Optimize workforce, renewable supply, roles, and targets jointly on outcomes.
   Replay action imitation and isolated TRAIN wrappers remain closed.
5. **Treat long-door geometry as a stratifier first.**  Measure whether banking cadence or task
   commitment, rather than pathfinding, explains residual loss before implementing anything.

## Evidence

- `phase21-control-field-census-2026-07-18.json`;
- `recent_resident_field_census.py`;
- `opponent-crop-controlled-transfer-protocol-2026-07-18.md`.
