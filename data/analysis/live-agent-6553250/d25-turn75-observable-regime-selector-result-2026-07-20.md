# D25/D25a observable turn-75 regime selector — result (2026-07-20)

## Verdict

**Close the frozen observable selector before prospective data.**

The original D25 development gate passes strongly, but its no-retuning cross-factor audit misses
the frozen precision floor: **73.23% versus 75%** when both a map block and a structural opponent
family are unseen.  Every value and tail gate still passes, making this an important near-pass,
but the explicit D25a rule forbids opening seeds 50,120--50,179 or choosing another development
configuration.

No candidate, source integration, submission, Arena game, or resident change occurred.

## Integrity

- Two consumed five-seed feature exports are byte-identical.
- The development export contains 1,920/1,920 unique seed/seat/opponent keys and 426 observable
  features, 359 of which vary.
- All rows reach turn 75 and exactly match D24 root scores, wood, workers, plant count, and cut
  status; there are zero mismatches.
- No seed, seat, opponent identity/index, agent identity, command text, future state, or terminal
  field enters the model matrix.
- Reversing every input row reproduces the selected model's out-of-fold predictions exactly.

The Rust exporter has six focused tests passing.  The Python analyzer compiles under the project
virtual environment.  Four unrelated pre-existing Rust library warnings remain unchanged.

## Frozen D25 result

The consumed D24 corpus contains 1,077 positive option cells out of 1,920 (56.09%).  A hindsight
positive-cell oracle is worth +50.477 seed-clustered margin.  The fixed 21-model × 5-buffer grid
evaluates 105 configurations; 37 pass both original schemes.  The predeclared ordering selects
`random_forest_d4_l40_b30`.

| Out-of-fold scheme | Switch rate | Precision | Margin | 95% interval | Worst opponent | Catastrophe rate | Negative mass ratio | Oracle captured |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Six blocked map folds | 49.27% | 77.17% | +32.431 | [+23.769, +41.092] | +21.167 | 9.90% vs 15.00% | 0.731 | 64.25% |
| Eight held opponent folds | 50.21% | 81.54% | +36.738 | [+28.031, +45.445] | +24.263 | 9.01% vs 15.00% | 0.679 | 72.78% |

All eight opponent means are positive in both schemes.  The result shows that a large fraction of
the D24 option value is genuinely predictable from visible shared-prefix state, rather than only
from opponent nickname or hindsight outcomes.

## D25a cross-factor audit

The initial opponent split had two optimism channels: Compact Gold and fixed Gold are behavioral
aliases, and the map and opponent exclusions were marginal rather than simultaneous.  D25a froze
the selected model and buffer, grouped the aliases, and allowed no retuning.

| Audit | Switch rate | Precision | Margin | 95% interval | Worst opponent | Catastrophe rate | Negative mass ratio | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Seven structural-family holdouts | 49.53% | 80.86% | +36.103 | [+27.267, +44.940] | +21.017 | 9.53% | 0.704 | pass |
| 6 map blocks × 7 structural families | 50.00% | **73.23%** | +28.888 | [+20.262, +37.513] | +18.400 | 10.94% | 0.785 | **fail precision** |

The crossed audit selects 703 beneficial, 253 harmful, and 4 neutral cells.  Its mean, trimmed
mean, interval, all-opponent, worst-opponent, catastrophe, negative-mass, selection-rate, and
57.23%-oracle-capture checks all pass.  Only positive precision misses, by 1.77 percentage points.
Both audit prediction streams repeat bit-for-bit after row reversal.

## Analysis by abstraction level

### Statistical

Separate map and opponent CV was optimistic but not fictitious.  Joint exclusion reduces value
from +32--37 to +28.89 and precision below the conservative floor, while retaining a strongly
positive interval.  The selected policy is valuable on average, but approximately one in four
switches remains harmful under the closest local analogue of simultaneous map/opponent transfer.
That is too much concentrated risk for a top-three objective.

### Behavioral

The full 256-tree forest contains 3,039 split nodes, 3,295 leaves, and uses 326 of 359 varying
features.  Its most frequent/root features are own second-worker chop level, initial iron and
plum, shack separation, own worker movement, near-shack fruit, and turn-25/50/75 geometry.  It is
therefore learning **resident/farm compatibility of the induced map and worker architecture** at
least as much as opponent regime.  This explains why held-family transfer is strong but joint
new-map transfer loses precision.

### Strategic

The result reinforces D24: the useful option is a two-worker scheduling change, not late worker
expansion.  Roughly half the shared turn-75 states benefit substantially from production mode,
and conservative selection suppresses much of the tail.  But compatibility is distributed across
many geometry and trajectory details rather than one stable opponent-growth threshold.

### Deployment

Even without the precision miss, a 3,039-split forest using 326 features plus the complete
ownership-aware farm would be difficult to add to a 62,725-byte resident under the 100 kB cap.
The research result is an architecture microscope, not a slim candidate.  Compressing this failed
boundary would also violate the frozen no-capacity/no-retuning rule.

## Consequence and next hypothesis

Close D25 at this representation.  Do not lower the buffer, lower the precision gate, select one
of the other 36 passers, add opponent identity, enlarge the forest, or open the reserved block.

The next eligible mechanism is not another classifier.  Test a **bounded production pulse**:
resident through turn 74, the exact `ownership2` whole policy for a fixed 25/50/75-turn interval,
then a cold visible-state resident restart through terminal play.  This directly constrains the
measured farm downside instead of predicting it, while retaining the turn-75 production window.
It is distinct from the rejected permanent handoff and failed unit-component swaps.  Durations
must be selected only on already-consumed maps, then frozen before any new block.

## Evidence

- `d25-turn75-observable-regime-selector-protocol-2026-07-20.md`;
- `d25-turn75-features-smoke-0-4.tsv` and repeat TSV;
- `d25-turn75-features-development-50000-50119.tsv`;
- `d25-turn75-regime-selector-development-50000-50119.json`;
- `d25a-selector-cross-factor-audit-protocol-2026-07-20.md`;
- `d25a-selector-cross-factor-audit-50000-50119.json`;
- `rust/src/bin/d25_turn75_features.rs`;
- `cgauto/d25_turn75_regime_selector.py`;
- `cgauto/d25_cross_factor_audit.py`.

SHA-256:

- feature TSV: `64aad6130b1e6c76d71b58fc46743df316534cfdba7100546552ff246a655837`;
- D25 JSON: `0aa82df365f35abc6ea136105ccf33394f754357bfd171b91650430993a70027`;
- D25a JSON: `c325465279039e1a42b89623e7ab1cf1665828b0986df453c6f77f19ebae906f`.
