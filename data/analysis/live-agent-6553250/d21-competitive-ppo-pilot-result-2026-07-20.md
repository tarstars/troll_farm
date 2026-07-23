# D21 competitive closed-loop PPO pilot — result (2026-07-20)

## Decision

**FAIL.  Close the checkpoint; do not qualify, promote, submit, or test it in Arena.**

The run completed correctly, but the final policy is worse than the unchanged accepted D11 actor
on the exact same 960 reserved seeds.  It failed two preregistered gates:

1. mean margin needed to improve by at least +5, but changed by **-2.685**; and
2. at least four of six opponent means needed to improve, but only one improved.

The machine-readable verdict is `d21-competitive-ppo-pilot-gate-2026-07-20.json`.

## Execution integrity

- exact initialization: D11 checkpoint SHA-256 `44c9a9ed...38d8de6`;
- model seed 2107 and training stream beginning at 8,200,000;
- exactly 1,000,000 transitions in 100 updates of 100 x 100 decisions;
- wall time 1,168.27 seconds and 855.96 transitions/second;
- zero intermediate validation evaluations;
- zero illegal actor actions in training;
- 1,000,000 / 1,000,000 legal auxiliary-teacher labels;
- finite losses, parameters, rewards, and final evaluation;
- final checkpoint SHA-256 `d51dd992...1f78c8cb`; and
- exact reserved evaluation seeds `[8,100,000, 8,100,960)`, all ending at turn 300.

Thus this is an optimization result, not an implementation or environment failure.

## Frozen validation comparison

| Metric | Initial D11 | Final D21 | Change |
|---|---:|---:|---:|
| Mean margin | **+18.895** | +16.209 | **-2.685** |
| Win rate | 59.27% | 58.65% | -0.63 pp |
| Mean own score | 150.245 | 147.408 | **-2.836** |
| Mean opponent score | 131.350 | 131.199 | -0.151 |
| Training completion | 99.79% | 98.33% | -1.46 pp |
| Crop creation | 97.71% | 89.38% | **-8.33 pp** |
| Renewable harvest | 98.23% | 94.90% | -3.33 pp |
| Margin <= -100 | 71 | 86 | **+15** |
| Illegal actions | 0 | 0 | 0 |

Almost the entire margin regression is lost own production, not an opponent response: own score
falls 2.836 while opponent score falls only 0.151.

## Paired distribution

The final policy improves 449 seeds, ties 82, and regresses 429.  The median delta is zero, but
the negative tail is heavier:

- mean `-2.685`, standard error `1.131`;
- descriptive normal 95% interval `[-4.902, -0.469]`;
- q10 / q25 / q50 / q75 / q90: `-37.1 / -9 / 0 / +9 / +27`;
- 72 regressions of at least -50 versus 38 improvements of at least +50; and
- minimum / maximum: `-210 / +153`.

The failure is therefore not caused by a few harmless ties or one extreme outlier.  PPO made
many useful and many harmful changes, with asymmetric downside.

## Where performance moved

| Opponent | Margin delta | Own-score delta | Opponent-score delta |
|---|---:|---:|---:|
| Complete baseline | **-6.235** | **-6.651** | -0.416 |
| Renewable planter | -1.488 | -2.590 | -1.102 |
| One-shot reaper | -2.630 | -1.178 | +1.452 |
| Funded pair | -1.988 | -2.760 | -0.772 |
| Sustained funded trio | **+0.815** | -0.254 | -1.069 |
| Repeated pressure + reacquisition | **-5.077** | -3.606 | +1.472 |

Only sustained funded trio improves.  The strongest recipe regressions are standard chopper
`-7.560` and hybrid chopper `-8.234`; only cheap planter `+1.008` and the level-one anchor
`+2.690` improve.  This is broad production-policy erosion, not successful specialization against
the hard baseline opponent.

## Abstraction-level conclusions

### Environment and objective

The Level-6 environment is viable.  Its rewards telescope exactly to terminal score margin, it
supports mixed strategic opponents, and both D11 and the teacher strongly beat random.  D21 did
not fail because the task was saturated or mechanically impossible.

### Optimizer

Per-update PPO diagnostics looked healthy throughout: KL remained below 0.03, the critic learned,
and the late sampled-policy margin recovered after a mid-run trough.  These local diagnostics did
not protect terminal deterministic performance.  A per-update trust region is not a trust region
around the accepted policy after 100 cumulative updates.

### Representation and policy

The network moved materially: total relative parameter L2 drift is 8.63%; stem 9.62%, residual
tower 7.54%, critic 9.81%, and the small actor head **21.64%**.  The 0.05 teacher auxiliary retains
basic mechanics but does not preserve productive scheduling or tail safety.  Updating the whole
shared policy trades coherent D11 behavior for a mixture of locally plausible changes.

### Strategic implication

Another unconstrained end-to-end PPO replica is not the next move.  The evidence favors
**conservative policy improvement around D11**: keep the accepted policy byte-for-byte as the
fallback, identify individual disagreements with exact terminal continuations, and permit only
sparse deviations whose paired downside is understood.  This also reconnects the PPO line with
the project's Monte Carlo work without reviving throughput-starved whole-plan RHEA.

## Next experiment

D22 should causally evaluate D21's action disagreements one at a time on shared D11 states:

1. follow D11 on fresh discovery seeds;
2. select deterministic D11-vs-D21 disagreements across four game phases;
3. replay exactly one D21 action, then return to D11 through turn 300;
4. pair each terminal result with the unchanged D11 continuation; and
5. measure whether D21's individual changes are directly harmful or locally useful but destructive
   only when compounded.

If individual deviations are also negative, close this PPO action proposal.  If a sparse robust
positive subset exists, the next controller should be a confidence-gated residual with exact D11
fallback—not another replacement policy.
