# D106a q6 fresh-map proposal readout — result

Date: 2026-07-22  
Decision: **q6 action basis passes; close the fixed offline ridge readout**

## Outcome-blind precision adjudication

The second untouched panel contains 230 eligible roots. On the same roots, q4 exposes 17.396
unique noncontrol proposals per root and 48 active experts; q6 exposes 16.609 and 50 active experts.
Both have a minimum of eight proposals and joint coverage at every root. Q6 retains 85.85% of q4's
union per root on average, never less than 57.14%, with 78.47% mean Jaccard similarity. It retains
all semantic breadth and fits in 9,180 conservative base85 bytes.

Every frozen selection gate passes, so q6 is locked before terminal access. Existing q6 proposals
from the consumed D105a panel remain uninspected.

## Fresh q6 headroom

Two independent 4,050-arm continuation matrices and their 256-task D40 controls are byte-identical.
All source, lock, action, terminal, control-parity, mechanics, crop, and worker checks pass.

The fresh q6 union fully replicates causal headroom:

| Measure | Result |
|---|---:|
| Mean margin gain over D40, all tasks | **+32.047** |
| Strict rooted improvements | **216/230 = 93.91%** |
| Mean own-score delta | +17.348 |
| Mean opponent-score delta | -14.699 |
| Worst family gain | **+17.813** (`resident`) |
| Increment over complete best-single, rooted | **+12.017** |
| Joint strictly beats best-single | **145/230 = 63.04%** |
| Crop / worker-three rate | 100% / 93.75%, exactly D40 workforce |

Winning proposals span all jobs, every observed provenance class, both seats, all families, and
reversed worker order. This is independent new-map evidence that the proposal action abstraction
is real; D105a's result was not merely a consumed-panel artifact.

## Discovery-only readout

The fixed no-intercept ridge trains on 1,957 noncontrol arms from 120 discovery roots. Its combined
semantic-plus-endorsement representation is better than either frozen ablation, but does not
calibrate safe abstention on 110 held roots:

| Held measure | Combined | Semantic only | Endorsements only | Gate |
|---|---:|---:|---:|---:|
| Mean gain, all 128 tasks | **+2.555** | +1.727 | +1.859 | >=+2 |
| Activation | **87.27%** | 89.09% | 76.36% | 15%--80% |
| Positive among activated | **54.17%** | 48.98% | 45.24% | >=55% |
| Oracle capture | **8.44%** | 5.70% | 6.14% | >=15% |
| Positive families | **5/8** | 4/8 | 6/8 | >=6 |
| Worst family | **-11.375** | -7.125 | -4.875 | >=-3 |

The combined model still improves 47.27% of held rooted tasks, uses broad joint actions, preserves
all crops and workforce, and achieves a positive overall mean. Its failure is selective authority:
it predicts too many proposals above zero and concentrates losses against `script_boss` and
`compact_gold`. The fixed zero threshold cannot be tuned after these outcomes.

## Interpretation and next move

Q6 resolves the compact action-generator question. The remaining bottleneck is no longer proposal
coverage, causal value, mechanics, or source size. It is learning when to retain D40 versus grant
authority to a proposal under trajectory-level opportunity cost.

Close the clipped one-deviation ridge exactly as tested. Do not tune its threshold, alpha, target,
features, or opponent-specific corrections on this consumed validation set. Retain q6 and the
validated feature/action ABI. The next eligible experiment is direct online learning on new maps:
a small recurrent controller with explicit D40 fallback, bounded intervention budget, variable
deduplicated proposal actions, and whole-episode paired objectives. It must first pass mechanics,
activity, optimization-signal, and prospective fixed-policy gates before packaging or platform use.

No candidate, platform action, submission, or resident change occurred.
