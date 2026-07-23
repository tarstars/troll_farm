# D22 D21-disagreement Monte Carlo — result (2026-07-20)

## Decision

**MIXED UNSAFE.  Close the D21 action proposal; do not build a residual or distill these labels.**

The diagnostic was valid and well covered, but D21's individual disagreements do not contain the
robust causal signal preregistered for either a compounding diagnosis or a sparse residual path.
The machine-readable result is
`d22-d21-disagreement-monte-carlo-gate-2026-07-20.json`.

## Readiness

All five readiness gates passed:

- 240 discovery-only seeds `[8,300,000, 8,300,240)`;
- 138,275 shared D11 states inspected;
- 9,263 raw D11-vs-D21 disagreements;
- 884 outcome-blind selected events, balanced 218 / 223 / 226 / 217 across the four turn bands;
- opponent coverage 120--201 events and recipe coverage 77--158;
- byte-identical all-D11 terminal rows on repeat;
- exact pre-intervention observation+mask signatures on every replay;
- zero illegal D11, D21, or replay actions;
- zero missed or duplicate interventions; and
- all baseline and counterfactual episodes finite at turn 300 with exact reward identity.

This is a policy conclusion, not an instrumentation failure.

## One-action causal result

Each row applies exactly one D21 action on a shared D11 state, then returns permanently to D11.

| Metric | Result |
|---|---:|
| Interventions | 884 |
| Mean terminal-margin advantage | **+0.018** |
| Median | 0 |
| Positive / zero / negative | 15.16% / **69.23%** / 15.61% |
| Gain at least +10 | **5.09%** |
| Loss at most -10 | 4.98% |
| q10 / q25 / q50 / q75 / q90 | -2 / 0 / 0 / 0 / +3 |
| Worst-decile mean | -14.886 |
| Minimum / maximum | -111 / +86 |
| New catastrophes | 2 / 884 = 0.23% |

The near-zero mean is not the preregistered compounding result.  Only three of six opponent means
are nonnegative and the positive rate is far below 30%.  It is also not the sparse-opportunity
result: only 5.09% gain at least +10 versus the required 20%.

## Time structure

| Referee turns | Events | Mean | Positive | Gain >= +10 | Worst decile |
|---|---:|---:|---:|---:|---:|
| 0--74 | 218 | +0.156 | 27.52% | 12.84% | **-32.190** |
| 75--149 | 223 | +0.112 | 17.49% | 4.48% | -14.091 |
| 150--224 | 226 | -0.177 | 9.29% | 2.65% | -8.545 |
| 225--299 | 217 | -0.014 | 6.45% | 0.46% | -2.905 |

Early disagreements have the only material upside, but also the worst downside and a -111
minimum.  Late policy differences are overwhelmingly terminal-neutral.  This explains why a
large actor-head change can produce many different commands without creating corresponding score
value.

## Opponent structure

| Opponent | Events | Mean advantage | Positive rate | Gain >= +10 |
|---|---:|---:|---:|---:|
| Complete baseline | 139 | -0.201 | 16.55% | 10.07% |
| Renewable planter | 135 | +0.007 | 11.11% | 1.48% |
| One-shot reaper | 152 | -0.382 | 11.84% | 3.29% |
| Funded pair | 137 | +0.270 | 14.60% | 5.84% |
| Sustained funded trio | 201 | +0.990 | 18.41% | 5.47% |
| Repeated pressure + reacquisition | 120 | **-1.125** | 17.50% | 4.17% |

D21's only full-policy validation improvement was sustained funded trio, and its one-action
proposals are also best there.  The changes are negative against three opponent families,
including repeated pressure and complete baseline—the main strategic weaknesses.

## Conclusions at different abstraction levels

### Action level

Most D21 disagreements merely exchange equivalent movement targets or timing without changing the
terminal result.  The nonzero tail is almost symmetric in frequency, but the early downside is too
large for ungated use.

### Closed-loop level

The full D21 loss is caused by repeatedly compounding a very weak action signal.  D22 does not show
that individual changes are broadly good; it shows that they are mostly neutral, occasionally
useful, and occasionally destructive.  Autoregressive drift turns this low signal-to-noise ratio
into lower production and more catastrophic games.

### Learning level

PPO's local surrogate and per-update KL can confidently move probabilities among actions that are
terminally equivalent on most states.  The 21.64% actor-head drift is therefore not evidence of
policy improvement.  A teacher auxiliary preserves legality and recognizable mechanics, but not
the long-horizon value ordering among equivalent-looking actions.

### Project level

This closes the current **D11 -> D21 PPO -> D22 Monte Carlo residual** branch.  It also avoids
repeating D16--D19: those experiments already showed that sparse one-intervention labels could not
be distilled safely around the resident, and D22's stronger PPO-proposed alternatives have even
less qualifying positive density.

## Next move

Return to actual-resident strategy and statistics, not another low-level controller learner.
The next useful iteration should refresh the real loss taxonomy and first-move/worker-architecture
gap against strong agents, then identify a complete coherent branch whose advantage is visible
before policy trajectories diverge.  Any new branch must preserve the stable resident and use
actual terminal outcomes; D21/D22 provide no candidate and no Arena authorization.
