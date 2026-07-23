# Complete-economy representation smoke — result, 2026-07-19

## Verdict

**Close the fixed Gold-style farm-economy grammar.  Do not open confirmation seeds 30--59.**

All integrity checks pass, and the grammar expresses highly productive closed-loop economies, but
none of its 31 fixed genomes clears the frozen opponent-robust discovery gate.  The best overall
genome beats resident by +82.792 mean margin and +89.521 trimmed margin across 480 cells, yet loses
-47.933 against adaptive Gold.  Its seven other opponent means are all strongly positive.

The result is informative but not eligible for threshold relaxation, portfolio fitting, catalog
expansion, fresh data, candidate packaging, platform games, arena submission, or resident change.

## Integrity

- 31 unique labels and 31 unique complete configurations;
- 30 consumed discovery seeds × both seats × eight opponents = 480 cells per genome;
- 14,880 candidate rows plus paired resident outcomes;
- the grammar's `Resident` atom and a direct `SecureOrchardBot::new()` instance emit identical
  non-MSG commands throughout every resident-control stream;
- all games complete under the corrected terminal/stall rule without panic; and
- the run used all 20 available CPUs (observed 1,946% process CPU).

## Discovery leaders

| Genome | Mean margin delta | Trimmed delta | Nonnegative opponents | Worst opponent | Own score delta | Wood delta | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| `lean_m2c2h0k2` | **+82.792** | **+89.521** | 7/8 | -47.933 | +164.565 | +40.329 | fail worst |
| `lean_m2c3h0k2` | +66.073 | +72.940 | 7/8 | -66.200 | +148.629 | +36.913 | fail worst |
| `lean_m2c2h0k3` | +56.704 | +63.954 | 7/8 | -66.367 | +137.904 | +33.748 | fail worst |
| `lean_m1c2h0k2` | +50.475 | +59.396 | 7/8 | -77.233 | +136.804 | +32.865 | fail worst |
| `farm3_hold0_cap12` | +47.198 | +53.236 | 6/8 | -93.667 | +136.771 | +33.198 | fail worst |
| best four-worker genome | +38.988 | +40.630 | 6/8 | -66.917 | +121.250 | +31.156 | fail worst |

Every leader passes all discovery checks except the frozen worst-opponent floor.  This is not a
weak mean effect or inactive representation; it is a concentrated architectural counterexample.

## The decisive counterexample

The top genome is the existing two-worker `2/2/0/2` lean farm economy.  Against adaptive Gold on
the 60 seat cells:

| Mean outcome | Resident | Farm genome | Change |
|---|---:|---:|---:|
| Our score | 202.500 | 390.183 | +187.683 |
| Opponent score | 139.300 | 374.917 | **+235.617** |
| Margin | +63.200 | +15.267 | **-47.933** |
| Our wood | 48.467 | 94.917 | +46.450 |
| Opponent wood | 32.917 | 92.883 | **+59.967** |

The farm controller nearly doubles our wood and still wins those games in absolute terms, but it
raises the opponent even more.  Resident's lower-output denial economy holds a +63 edge; shared
supply turns that into only +15.  The frozen gate correctly rejects optimizing our production
while making the opponent's production cheaper.

Against the other seven families, the same genome's margin deltas range from +48.383 to +147.300.
The failure is therefore a sharp opponent-policy interaction, not general policy collapse.

## Analysis by level

1. **Representation:** exact fallback works, and complete stateful genomes create workers, plant
   about 40--58 trees, harvest, chop, and bank on their own induced trajectories.  The smoke is not
   another teacher-state imitation failure.
2. **Productivity:** the top two-worker genome gains +164.6 own score and +40.3 wood overall.  A
   complete renewable economy is expressible and locally powerful.
3. **Game theory:** trees are shared assets.  Production without access control, denial, or
   opponent-relative liquidation can increase both sides while reducing our edge.
4. **Workforce:** larger three- and four-worker genomes do not remove the counter.  Workforce,
   supply volume, and hold horizon are not the missing dimensions inside this grammar.
5. **Robustness:** seven positive opponent means cannot override a predeclared -47.9 counter when
   the rank-3 objective requires strength against worker-rich sustainable bots.
6. **Model validity:** adaptive Gold is also only a synthetic continuation.  Earlier calibration
   showed that the eight-model zoo poorly covers arena first actions and targets.  We cannot safely
   either ignore this counter or optimize harder against it until its relation to the field is
   measured.
7. **Search design:** closed-loop terminal outcomes expose the shared-supply externality that
   production proxies, imitation accuracy, and short horizons miss.  The evaluation architecture
   is worth retaining even though this fixed policy grammar closes.

## Next iteration

Run a **full-trajectory field-continuation coverage audit** on the consumed 160 Phase 21 candidate
games.  On each exact official initial map, replay the fixed local continuation zoo against exact
`b100_e6` and compare its opening, workforce, planting, harvest, chopping, score, and wood
trajectory to the actual arena opponent.  The immediate question is whether adaptive Gold covers
the catastrophic worker-rich field cohort or is merely a local adversarial artifact.

That audit may nominate missing coherent opponent archetypes, but it cannot tune or resurrect a
farm genome.  A new policy grammar requires a new causal architecture—such as private/denial-aware
supply—not parameter changes to this consumed catalog.

## Evidence

- `complete-economy-representation-smoke-protocol-2026-07-19.md`;
- `complete-economy-discovery-0-29.tsv` and `.json`;
- `rust/src/bin/complete_economy_search.rs`;
- `cgauto/complete_economy_representation_study.py`.
