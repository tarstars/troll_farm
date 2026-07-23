# D162a resident-native bounded capital option — result

Date: 2026-07-23  
Decision: **close the exact one-lane reserve interface as a scaling mechanism**

## Integrity and execution

D162 evaluates exact resident plus 12 frozen reserve options on 128 already-consumed tasks: maps
`9,844,136--9,844,143`, both seats, and eight opponent families. The one-worker and 20-worker
matrices contain exactly 1,664 rows and are byte-identical at SHA-256
`3fb3e3720777ac90f9d8c95605f72d8e7cfa9d96796987a337791ad1fdce21cd`.
The parallel run finishes in 15.828 seconds versus 156.990 seconds for one worker, a 9.9x wall-time
speedup.

Exact resident reproduces D161 on all 128 tasks with zero mismatch across scores, returns,
workforce, crops, mechanics, action hashes, and state hashes. Every option matches the resident's
state and action prefix exactly at its frozen activation turn. All 12 arms activate in all 128
tasks and change every terminal action hash. There are zero command-legality, affordability,
TRAIN-transaction, provenance, ambiguous-birth, worker-cap, horizon, or restart failures. Every
row has exact reward identity and no task exceeds three own workers.

The focused D160--D162 Python suite passes 11/11; the unchanged D102 and new D162 Rust suites pass
7/7. D162 makes no YT or platform request. The canonical YT root remains
`//home/delivery_ml/research/tarstars/troll_farm`, and reserved maps
`9,844,200--9,844,215` remain untouched.

## Scaling mechanism result

The interface does not fund worker three broadly enough:

| Arm family | Arms | Successful third workers | Best arm rate | Mean initial deficit | Best mean closest deficit |
|---|---:|---:|---:|---:|---:|
| Minimal `1/1/0/1` | 6 | 10 / 768 | 5/128 = 3.91% | 6.62--6.95 | 3.21 |
| Balanced `2/2/0/2` | 6 | 0 / 768 | 0% | 15.50--15.84 | 10.99 |

Four minimal arms train at least once, but no arm reaches the frozen 10% rate and balanced never
trains. The ten successes span both seats but only five opponent families. Thus the required four
10%-training arms and six-family breadth gates fail. Seventy-six active rows terminate naturally
before their deadline; this is reported, not a lifecycle failure.

The result strengthens D160 rather than contradicting it. One temporary acquisition lane reduces
the minimal bill deficit, occasionally to zero, but usually cannot outproduce ongoing resident
consumption and the opportunity cost before its 32/64-turn bound. The balanced bill remains at
least five units short in every task. Do not lengthen horizons, add a second lane, retune starts,
expand onto the remaining D161 maps, or train a selector under the D162 protocol.

## Descriptive resident-relative value

The failed scaler contains a separate and useful signal. A crop-safe per-task terminal envelope
over resident and all 12 options gives:

| Metric | Result |
|---|---:|
| Mean / median margin gain | +12.656 / +8.000 |
| Map-cluster normal 95% interval | [+8.965, +16.348] |
| Strict improvements / ties / regressions | 86 / 42 / 0 |
| Own-score / opponent-score delta | +6.234 / -6.422 |
| Positive families; worst family | 8/8; +8.063 |
| Positive seats / two-map blocks | 2/2; 4/4 |
| Crop creation | 100% resident; 100% envelope |
| Catastrophes | 4 resident; 2 envelope |
| Negative-margin mass | 645 resident; 510 envelope |
| Selected worker-three rate | 1/128 = 0.78% |

All 12 fixed arms are negative on average (`-7.625` to `-13.930`) and individually regress more
often than they improve. The positive envelope is therefore heterogeneous and not selectable as a
fixed policy. Crucially, only one of 86 selected improvements reaches worker three. The value comes
from bounded resource routing/protection while retaining exact resident fallback, not from scale.
It passes every frozen capacity condition except the required 10% selected worker-three rate, but
the mechanism conjunction correctly prevents expansion.

## Next move

Close D162 as a capital option. Do not rescue it with result-dependent horizons, specs, starts, or
an outcome selector.

Retain one new hypothesis for a separately frozen experiment: exact-resident-native temporary
resource control may have causal value independent of TRAIN. Before implementing another policy,
perform a component-level audit that distinguishes directed fruit harvest/banking, IRON routing,
and suppression of resident resource consumption. Any causal ablation must use a different
already-consumed panel, keep exact resident KEEP explicit, use bounded interventions, and require
resident-relative value and tail safety. It must not claim workforce improvement or reuse D162's
per-task winners as labels.

## Reproducibility

- protocol SHA-256: `2deae13b36aa713f2334661a558d00917e364d8b25117d18cdc6e20bdf7ad7de`;
- lock SHA-256: `4dd5182384e90212d78811c6b61286536389d084a57a1e813060eee3124e4ab9`;
- runner SHA-256: `8c82a27191ecb999c945d969cd525afcd0073caaa1c2f5412cdca9d136879668`;
- analyzer SHA-256: `6c8b7a4220a25903ace7321894bbef4ea4644064da82440f79ad500199d63232`;
- machine-result SHA-256: `013a8a6c6cab5892a17e4b7e58da77aa11e2d7cf4b145e940f08d5158aed7f5c`.
