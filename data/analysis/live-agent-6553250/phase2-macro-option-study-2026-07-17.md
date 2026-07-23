# Phase 2 macro-option study — 2026-07-17

## Decision

**Reject farm-first orchard scale and explicit adaptive funding. Retain one sparse immediate-
worker mechanism for Phase 3 discovery, with the promoted stack as exact fallback.**

The surviving mechanism is not the reconstructed top-bot hybrid as originally proposed.  Under
the promoted Yamo continuation, paid harvest power was unused.  The useful intervention is:

1. snapshot the independently maximum-affordable turn-one movement/carry/harvest/chop levels;
2. consider entry only in the `1/2/2/*` affordability cell;
3. enter only when the promoted opening would wait for a `1/3/0/*` worker;
4. train an immediate `1/2/0/chop-max` worker and then return to the promoted controller.

This rule was derived and measured on reused discovery seeds.  It is not prospective evidence
and does not authorize an arena write.

## Control and scope

- Control: full strategy reference
  `candidate-agent6553250-preseed-orchard-coverage.min.rs`, behavior-identical to current slim
  arena resident `6557204`.
- Opponent zoo: `chopharvest`, `race`, `ringfix3`, `taskplan`, `yield`, and legacy `motion`.
- Independent unit: map seed; both seats are averaged inside every policy/opponent cell.
- All option changes used reused seeds beginning at zero.  No untouched block was consumed.
- Legacy `motion` varies across fresh processes because of randomized hash iteration.  It is
  retained as a robustness perturbation, but causal means below use the five deterministic
  opponents unless explicitly stated.

An early aggregation compared candidates with the older recovered artifact named `live` by the
league runner.  Final numbers in this report are recomputed against the promoted stack.  This
baseline correction does not change any rejection.

## Option A — farm-first orchard scale

The complete option trained a variable farmer on turn one, assigned the starter and farmer to
training-resource supply, targeted two fixed `2/2/0/2` choppers at staged deadlines, and handed
workers back to the promoted controller after completion or timeout.

Across ten discovery seeds, two process replications, and five deterministic opponents it
measured:

| Estimand | Result |
|---|---:|
| Paired score delta vs promoted stack | **-97.57** |
| Paired wood delta | **-27.46** |
| Positive / tied / negative cells | 16 / 0 / 84 |
| Cell range | -296.0 to +94.5 |
| Positive seed means | seed 8 only, +28.9 |
| Opponent-mean range | -116.75 to -66.15 |

The mechanism telemetry explains the loss:

- all 240 candidate sides trained the farmer on turn one;
- only 148/240 trained the first chopper and 96/240 reached four workers;
- 92 sides timed out before the first chopper, 52 before the second, and 96 scaled;
- first-chopper funding was limited most often by PLUM (78 sides), LEMON (58), IRON (50), and
  APPLE (19), with resources allowed to co-occur;
- the option created 6,794 tree episodes: 6,633 candidate-favored, 161 contested, and zero
  opponent-favored;
- candidate workers captured 4,231 fruit and 9,720 wood from that supply, versus 213 fruit and
  710 wood captured by opponents.

Opponent theft was therefore not the failure.  Funding, role conversion, and displaced baseline
work cost more than the privately captured supply returned.  Option A is closed.

Primary telemetry:
`farm-first-option-study-2026-07-17.json`.

## Option B — adaptive max-bank opening

### Global forms

The first implementation bought the maximum-affordable first hybrid and actively diverted both
workers to a later `3/4/1/3` funding target.  A first-only ablation removed later funding; a
surplus form permitted a later train only if already affordable.

| Form | Deterministic cells | Score delta | Wood delta | Verdict |
|---|---:|---:|---:|---|
| max-bank first, harvest max | 50 | -12.98 | -2.74 | reject globally |
| explicit later funding | 50 | -56.78 | -14.82 | reject |
| surplus-only later checkpoint | 50 | -12.98 | -2.74 | inert checkpoint |
| max-bank first, harvest 0 | 50 | -7.22 | -1.32 | reject globally; retain for selector league |

The explicit funding form often destroyed maps where the first worker helped, including cases
where no later worker was ever trained.  The surplus checkpoint issued no extra train on the
first ten seeds.  Adding opportunistic fruit harvesting also failed: even an on-tree-only,
low-score form surrendered contested-tree timing and increased opponent wood.  Yamo cannot use a
paid hybrid stat by merely appending harvest candidates.

### Sparse entry refinement

The raw `1/2/2/*` affordability cell appeared on five of the first 60 discovery maps.  It was
bimodal: seeds 4 and 44 won broadly, seed 43 lost catastrophically, and seeds 23 and 32 were
slightly negative.  Tracing the promoted opening exposed a structural distinction:

- on the two winning maps, promoted Yamo waited for `1/3/0/*` while `1/2/*/*` was affordable;
- on two mild losses, promoted Yamo already wanted `1/2/0/*`;
- on the catastrophic loss, promoted Yamo wanted `2/3/0/*`, so the option sacrificed both speed
  and carry.

Restricting entry to the first case made the other three maps exact fallback.  Removing unused
harvest power improved both selected maps further:

| Selected worker | Active-map deterministic mean | Wood | W/T/L over five-map sparse block |
|---|---:|---:|---:|
| `1/2/2/chop-max` | +43.85 | +12.25 | 10 / 15 / 0 |
| `1/2/1/chop-max` | +54.35 | +14.90 | 10 / 15 / 0 |
| `1/2/0/chop-max` | **+57.75** | **+15.75** | **10 / 15 / 0** |

For harvest 0, active deterministic cells range from +38.5 to +91.0.  Active means by opponent
are +60.0 (`chopharvest`), +54.5 (`race`), +55.0 (`ringfix3`), +54.5 (`taskplan`), and +64.75
(`yield`).

The frozen discovery registry contains two selected maps out of 60.  Treating the other 58 as
their proven structural zeros gives a discovery projection of **+1.925 score** and **+0.525
wood** across the five deterministic opponents: 10 wins, 290 ties, and zero losses.  At the seed
level this is two wins and 58 ties; removing the larger selected seed still leaves +0.890 mean.
The ordinary symmetric five-percent trimmed mean is zero because it removes the sparse positive
tail, which is why the roadmap now requires a separate activation/benefit/downside analysis.

This is promising mechanism evidence, not an unbiased estimate: the entry comparison and harvest
ablation were chosen after inspecting the same discovery block.

Primary results:

- `adaptive-max-bank-cell122-discovery-2026-07-17.json`;
- `adaptive-max-bank-cell122-carry3-discovery-2026-07-17.json`;
- `adaptive-max-bank-harvest-ablation-2026-07-17.json`;
- `adaptive-max-bank-first-hp0-discovery-10.json`.

## Artifacts and parity

The current sparse research candidate is:

- full: `candidate-agent6553250-adaptive-max-bank-cell-122-carry3-hp0.min.rs`, 91,383 bytes,
  SHA-256 `32b7f6ba7958405c5436ce48ff2a5a7a464029bbd61a8ad53089a33e87372aea`;
- slim: `candidate-agent6553250-adaptive-max-bank-cell-122-carry3-hp0-slim.min.rs`, 63,561 bytes,
  SHA-256 `7b6ee387efccc00dab40e16de108b19f7750f07387053dfd7ca573ea7f108f23`.

Both compile standalone with `rustc --edition 2021 -D warnings -O` and remain under 100 KB.
Dynamic parity against `chopharvest` over seeds 0--59 established:

- full versus slim: 120/120 seed/seat streams command-identical through terminal play;
- promoted stack versus candidate: exactly 116/120 streams command-identical;
- the four intended divergences are turn-one TRAINs on seeds 4 and 44, both seats.

## Phase-2 verdict and next move

Phase 2 passes narrowly: one non-control opening activates as designed, preserves exact fallback,
has an explicit controller-compatible mechanism, and shows plausible robust payback on its
selected discovery states.  The farm-first and funded-expansion architectures remain rejected.

Proceed to Phase 3 using the global immediate max-movement/carry/chop, harvest-0 option as the
full-information alternative.  Run it on all 60 reused discovery seeds, compute the per-seed
hindsight oracle, and fit/evaluate a small cost-sensitive selector with blocked validation.
Freeze no prospective protocol until that league and selector analysis are complete.  Do not
submit or change the arena resident.
