# Improved E7a initial-state sector analysis

- Task context: `20260802-initial-state-sector-policy-audit`
- Analyst: `chatgpt_1`
- Date: 2026-08-02 UTC
- Branch: `agent/chatgpt_1-top-player-full-review`
- Original causal audit closeout: `8dc2f9d13b13c8cf8ccbb20d3964ac2539ee5288`
- Derived rows: `chatgpt_1/e7a-initial-sector-sign-preflight-2026-08-02.csv`
- Derived CSV SHA-256 before publication: `0c6b77a0221be2b17cd0fd8fc12d1189b544cf5a55fac6a1b079867e0ca082da`
- Platform/source mutation: none

## Verdict

**`MEASUREMENT_ONLY — EXPLORATORY_SIGN_SECTOR_FOUND; TERMINAL_VALUE_UNIDENTIFIED`.**

I performed the analysis proposed in the initial sector audit as far as the tracked evidence
allows. There is a reproducible, outcome-blind initial-state signal for the sign of the exact
E7 `typeToCut` FLIP intervention:

```text
default species = LEMON
and
sum_distance(PLUM) - sum_distance(LEMON) <= 8
```

Here `sum_distance(species)` is the exact E7 focus geometry: the sum, over all initial trees
of that species, of BFS distance from the resident shack's walkable doors. The current policy
chooses the smaller sum, with LEMON winning exact ties.

In leave-one-root-out analysis, a nested rule learner selected this exact sector in all 60
training folds. It marks 13/60 roots, of which 10 are among the 24 roots on which the committed
E7 hindsight oracle prefers FLIP:

- precision `10/13 = 76.92%`, Wilson 95% interval `[49.74%, 91.82%]`;
- recall `10/24 = 41.67%`, Wilson 95% interval `[24.47%, 61.17%]`;
- accuracy `43/60 = 71.67%`, Wilson 95% interval `[59.23%, 81.49%]`;
- balanced accuracy `66.67%`;
- inside-sector FLIP-preference rate `76.92%`, outside-sector rate `14/47 = 29.79%`;
- odds ratio `7.86`, two-sided Fisher exact `p = 0.00348`.

A 100,000-permutation test that repeats threshold/species selection inside every
leave-one-root-out fold gives:

- precision `p = 0.00477`;
- balanced accuracy `p = 0.01318`;
- accuracy `p = 0.00801`.

This is a real exploratory sign signal, not a policy-value result. The full root-level E7
margin rows were written to `/tmp` during the original audit and are not committed. The
tracked compact result preserves the 24 preferred-root labels but not their delta magnitudes.
Consequently I cannot compute the sector-conditioned terminal margin, regret versus the
hindsight oracle, seat/family effects, displacement, or tail safety. No source change,
candidate, fresh panel, or Arena action is justified.

## 1. Provenance and exact data boundary

The E7 closeout and manifest establish:

- 60 reused generated Bronze roots (`0..59`);
- six frozen opponent families, both seats;
- exact unchanged policy versus one-byte-anchored persistent LEMON/PLUM FLIP;
- 1,440 total games;
- blanket FLIP paired margin `-12.173611`;
- 24/60 roots selected by the seed-level hindsight oracle;
- seed-level hindsight ceiling `+10.509722`;
- positive leave-one-family-out evaluation in 6/6 families.

The committed compact JSON explicitly names the 24 preferred-FLIP roots:

```text
3, 8, 15, 16, 17, 18, 19, 20, 25, 26, 28, 32,
34, 37, 39, 42, 43, 45, 50, 52, 55, 56, 57, 58
```

The original analyzer's complete payload contains `geometry.rows`, `value_rows`, and
`oracle_rows`. However, the manifest records the complete jobs-8 and jobs-1 outputs only as:

```text
/tmp/e7-type-to-cut-j8.json
/tmp/e7-type-to-cut-j1.json
```

with hashes:

```text
jobs-8: 18648731768f0756c787ddc52fe83a547213e60e2f35e993b80d2fd45c7fea14
jobs-1: 288cd0a0d21dcf2437553b94dba936878f32ac3fe3380d38901476ec7aa26ca8
normalized payload: c7a9d614ca607227b1dfb9649783a034212b4446cf5838250768695dff0044a5
value rows: d3f3687945983c4809518388a0269db97d8a50c6ba6917fc12c63ef418410c76
```

The repository tracks only the compact aggregate result. Thus this analysis has exact
positive/negative root labels but not exact root-level treatment magnitudes.

## 2. Exact t0 reconstruction

I reimplemented only the tracked deterministic initial-state generator and static E7 geometry;
I did not run bot matches or simulate counterfactual games.

The reconstruction uses:

- `sim/mapgen.py` at the E7 closeout;
- `bot/main.py` constants and BFS semantics;
- `sim/engine.py` plant growth/health constants.

It exactly reproduces every published E7 geometry anchor:

| Anchor | Published | Reproduced |
|---|---:|---:|
| default LEMON roots | 35 | 35 |
| default PLUM roots | 25 | 25 |
| exact distance ties | 4 | 4 |
| seat-symmetric species choice | 60/60 | 60/60 |

This is a strong integrity check: the t0 feature rows are tied to the exact maps that generated
the 24 sign labels rather than to a similar map generator.

## 3. Outcome-blind features

All features are available before the first command. No outcome, terminal score, later
workforce, later inventory, opponent action, opponent family, or seat identity is used as a
selector feature.

The literalized primary feature vector contains ten FLIP-minus-default contrasts:

```text
default_is_lemon
starting-bank species difference
total-distance-sum difference
tree-count difference
tree-health difference
ripe-fruit difference
ETA-weighted health difference
ETA-weighted fruit difference
ETA-weighted 50-turn fruit-potential difference
water-adjacent-tree-count difference
```

The broader diagnostic inventory contains 29 intervention-specific contrasts, but model
selection always remains grouped by map root.

## 4. Primary fixed multifeature check — failed

A standardized ridge classifier with the ten primary features, fixed `alpha = 10`, evaluated
by leave-one-root-out prediction gives:

| Metric | Result |
|---|---:|
| predicted FLIP support | 20/60 |
| true positives / false positives | 11 / 9 |
| precision | 55.00% |
| recall | 45.83% |
| accuracy | 63.33% |
| balanced accuracy | 60.42% |
| ROC AUC | 0.6076 |
| average precision | 0.4654 |
| MCC | 0.2165 |

This fails the audit's proposed `>=65%` held-root precision gate. The broad t0 representation
does not qualify.

## 5. Feature-selection diagnostic

A second, explicitly diagnostic procedure performs feature selection separately inside each
leave-one-root-out training fold:

1. calculate the absolute training correlation for each of 29 t0 contrasts;
2. select exactly one feature;
3. fit a standardized one-feature ridge classifier with `alpha = 1`;
4. predict the untouched root.

`delta_dist_sum` is selected in **60/60 folds**. Results:

| Metric | Result |
|---|---:|
| predicted FLIP support | 20/60 |
| true positives / false positives | 13 / 7 |
| precision | 65.00% |
| recall | 54.17% |
| accuracy | 70.00% |
| balanced accuracy | 67.36% |
| ROC AUC | 0.6863 |
| average precision | 0.5394 |

The learned raw distance threshold ranges from `8.794` to `10.303` across the 60 training
folds, median `9.432`. A 100,000-permutation test that repeats feature selection in each fold
gives `p = 0.0262` for balanced accuracy, `0.0340` for accuracy, and `0.0851` for precision.
This supports the distance-gap variable, but not a high-confidence selector.

Univariate direction-corrected AUCs reinforce the interpretation:

| t0 contrast | AUC | beneficial-FLIP mean | other-root mean |
|---|---:|---:|---:|
| total distance gap | 0.7350 | 9.92 | 17.83 |
| ripe-fruit difference | 0.6962 | -0.17 | 2.67 |
| cooldown-sum difference | 0.6834 | 3.83 | 11.50 |
| tree-count difference | 0.6788 | 1.25 | 2.17 |
| health-sum difference | 0.6788 | 10.67 | 22.44 |

The alternate focus tends to help when changing species gives up relatively little initial
distance/asset advantage.

## 6. Interpretable nested sector rule

To test whether the species asymmetry is real rather than a post-hoc table observation, I used
a small nested rule class. Inside each training fold it considers only:

```text
group in {all roots, default-LEMON roots, default-PLUM roots}
distance-gap threshold from training values
20%..80% training support
```

It chooses the rule with highest training precision, then balanced accuracy, recall and
accuracy. It selects the same rule in all 60 folds:

```text
default species is LEMON AND distance gap <= 8
```

The out-of-fold confusion matrix is:

| | predicted CONTROL | predicted FLIP |
|---|---:|---:|
| FLIP not preferred | 33 | 3 |
| FLIP preferred | 14 | 10 |

The signal is asymmetric:

| Default species | roots | predicted support | precision | recall | balanced accuracy |
|---|---:|---:|---:|---:|---:|
| LEMON | 35 | 13 | 76.92% | 76.92% within LEMON positives | 81.64% |
| PLUM | 25 | 0 under the rule | — | 0% | 50% |

The rule reproduces in both arbitrary seed halves:

- seeds `0..29`: 4/6 precision `66.67%`;
- seeds `30..59`: 6/7 precision `85.71%`.

The nested 100,000-permutation results quoted in the verdict account for searching group and
threshold inside each fold. They do **not** account for the fact that this compact rule family
was designed after inspecting the diagnostic results. The rule is therefore exploratory and
must be frozen before any fresh-root evaluation.

## 7. Mechanistic reading

The current `typeToCut` rule chooses the species with the lower aggregate resident travel
distance. The new signal does not say that distance is irrelevant. It says:

> When LEMON wins the current distance comparison only narrowly, switching focus to PLUM is
> much more likely to have positive paired value.

Possible explanations include a LEMON tie/near-tie bias, species-specific asset value not
represented by the raw distance sum, or an opponent-control asymmetry. The sign-only artifact
cannot distinguish them. In particular, it does not reveal whether the positive roots gain
own score, suppress opponent score, or merely avoid a tail. Those questions require the
missing root/family delta rows.

## 8. Gate-by-gate disposition

| Required gate | Status |
|---|---|
| exact finite intervention | PASS — exact E7 FLIP |
| outcome-blind t0 features | PASS |
| root-grouped evaluation | PASS — leave-one-root-out |
| minimum support >=12/60 | PASS — 13/60 |
| primary held precision >=65% | **FAIL — 55%** |
| exploratory rule precision >=65% | PASS — 76.92%, but post-hoc |
| representation novelty vs D63/Phase15/D91 | PARTIAL — intervention-specific gap, manifest comparison still required |
| selected-arm value above best static | **UNAVAILABLE** |
| regret <=35% of hindsight oracle | **UNAVAILABLE** |
| both-seat value | **UNAVAILABLE for selected sector** |
| opponent-family holdout value | **UNAVAILABLE for selected sector** |
| displacement/opponent leakage | **UNAVAILABLE** |
| catastrophe and negative-mass safety | **UNAVAILABLE** |
| fresh prospective validation | NOT RUN |

The correct current state is not `SECTOR_PREFLIGHT_PASSED`. It is:

```text
E7a exploratory sign sector found;
primary multifeature gate failed;
terminal value blocked on missing compact root-level deltas.
```

## 9. Smallest exact next step

No new simulation is needed if either original `/tmp` jobs output still exists. A host-capable
agent should:

1. verify the jobs-8 or jobs-1 full JSON against the recorded SHA-256;
2. verify `value_rows`, `geometry_rows`, `divergence_rows`, and `oracle_rows` hashes;
3. publish a compact, non-trace table with one row per seed/opponent containing only:
   `seed`, `opponent`, `control_species`, `delta_paired_margin`,
   `delta_seat_margins`, `delta_policy_score`, `delta_opponent_score`,
   and `delta_paired_wood_edge`;
4. preserve the original consumed panel and do not rerun or retune it.

If neither full output survives, regeneration of the exact locked E7 analyzer is a separate
owner/integrator decision. It must use commit-pinned source and consumed seeds for
reconstruction only, never for a new selector claim.

Once the compact delta table is available, the already frozen exploratory rule can be priced
without fitting anything:

```text
C1 = FLIP iff default species is LEMON and distance gap <= 8
```

Report `C1-C0`, `C1-A1`, `C1-best_static`, root-bootstrap intervals, seat/family breakdown,
own/opponent score displacement, wood edge, catastrophes and negative-margin mass. Only after
that measurement can the integrator decide whether fresh prospective roots are warranted.

## 10. Reproducibility artifact

The committed derived CSV contains all 60 roots, the compact sign label, exact reconstructed
t0 contrasts, primary and diagnostic out-of-fold scores, and the frozen exploratory-rule
prediction. It contains no raw replay, sealed data, peer report, or post-command feature.

No source file, simulator, consumed counterfactual output, candidate, TestSession, Arena/API
endpoint, or submission was changed or invoked.
