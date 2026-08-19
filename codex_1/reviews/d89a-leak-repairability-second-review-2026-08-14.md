# D89a leak repairability: independent second review

- Reviewer: `codex_1`
- Date: 2026-08-14
- Scope: committed-evidence review only; no implementation, panel run, source edit, or Arena action
- Reviewed conclusion: `claude_1`'s restored `NOT_REPAIRABLE`
- Review verdict: **DISSENT — `UNRESOLVED`, strongly leaning `NOT_REPAIRABLE`**

## Owner summary

In plain terms: the evidence says D89a is unsafe and is a poor bet for more work, but it does not
prove that repair is structurally impossible. The strongest negative experiment increased the
number of opponent-crop target selections by 5.4 times and still moved opponent score slightly
upward. That closes the exact late targeting policy it tested. It does not close an unmeasured
production throttle, conversion-timing change, or a genuinely predictive conditional-activation
rule.

One numeric argument used to restore the closed verdict is invalid. The perfect-hindsight
70-task subset has mean opponent-score change `+0.829`, so it passes the frozen `<= +1` gate.
The cited `+8.002` is the upper end of an uncertainty interval after giving each of the 15
contributing maps equal weight. It is neither the gate named by the D89a protocol nor an upper
bound on what every possible selector can achieve.

Practical disposition: do not treat D89a as a candidate and do not claim its leak repaired.
Record the route as **not pursued because the prior is strongly negative and the missing tests
are expensive**, not as proven structurally impossible. This distinction matters because the
conditional-banana-farm design is an exposure limiter, not a demonstrated leak repair.

## Evidence boundary and provenance

I read the canonical task, the complete D89a analysis, both `chatgpt_1` reviews, the restoration
message and adversarial review, the D89a frozen inputs/result, the D92 result, and the owner's
conditional-banana-farm design.

The committed D89a files reproduce the hashes reported by the first review:

| input | SHA-256 |
|---|---|
| blueprint | `c3956d3bf33e51fb6a8a9b398a69bcdeea74b66c952eff1ced5144e200fbab04` |
| protocol | `65bb19bf438848c6f10cfb974a5687f4277eb4527fc63e8b0ef813714486af06` |
| result prose | `1762ccb16e89bf1a118088759bdfb7c3672ee6b252872eb8a5f4a8e7bc8d8b52` |
| discovery JSON | `d2bab93a609b99e621b265b5dec8261e98fb24f94cf2465d4a6e1b7d5887741a` |
| freeze | `c8ecfb77538844c40c4f73282af4f46401f67d396dc9fecc22f2d90b011ddde1` |
| analyzer | `6a4bb8971310d74777ef1491a73f95e40d72e89bd0355eddac6983ca1c6c75c8` |
| D92 result prose | `0e5084a05e65002b95d469d0e6e2da1c82d43549d0a7d9051646bf2eb6812f6c` |

Neither a D89a nor D92 panel TSV exists in this checkout. The required `medium_data` volume is
also absent. Therefore I independently recomputed every quantity available in the committed
D89a JSON, but I classify D92 row-level claims as measurements reported by its committed result,
not as independently re-derived raw-row measurements.

## Reproduced D89a facts

Arithmetic over all 256 committed pairs gives:

| quantity | reproduced mean |
|---|---:|
| own-score change | `+162.304688` |
| opponent-score change | `+82.863281` |
| margin change | `+79.441406` |
| own chopped-wood change | `+40.648438` |
| forced trained-role rewrites | `13.105469` per task; positive in 255/256 |

The family asymmetry also reproduces. `gold_adaptive` has own `+201.84375`, opponent
`+208.78125`, and margin `-6.9375`; the opponent gains more than we do. The aggregate leak is
therefore not a harmless accounting artifact, and the worst family is far more dangerous than
the pooled mean suggests.

The alleged theft-versus-opponent-own-production split remains **unresolved**. The aggregate
`+82.863281` exists in the JSON. The `+12.453 / +76.508` provenance split exists only in prose,
because the source rows carrying the necessary origin columns were not committed. A missing
decomposition weakens causal certainty; it does not erase the observed safety failure.

## Why the restored `NOT_REPAIRABLE` does not follow

### 1. The `+8.002` argument compares unlike estimands

I reproduced the oracle construction exactly: discard tasks with margin below `-60`, sort the
rest by opponent-score change, and take the largest prefix whose task-weighted opponent-score
mean is at most `+1`.

For the resulting 70 tasks:

- task-weighted opponent-score mean: `+0.828571`;
- own-score mean: `+130.785714`;
- margin mean: `+129.957143`;
- worst margin: `-56`;
- coverage: 15/16 maps, all eight families, both seats.

As a whole-panel conditional policy—zero change on the 186 abstentions—the opponent-score point
estimate is `+0.226563`, with a 16-map normal interval `[-0.621, +1.074]`. The whole-policy
margin is `+35.535156`, interval `[+14.248, +56.822]`.

The restoration's `+8.002` comes from a different calculation: first average selected tasks
inside each of only the 15 contributing maps, then give those map means equal weight. That
produces center `+2.608` and interval `[-2.786, +8.001]`. It changes both weighting and population.
It is a useful warning that the post-selected subset is uncertain. It is not the frozen
task-weighted `<= +1` gate and is not a perfect-hindsight “ceiling.”

The oracle is still not an implementable repair: it uses outcomes and therefore proves existence,
not predictability. But existence of a gate-clearing subset contradicts structural impossibility;
learnability remains an unanswered question.

For additional scale, the first 32 oracle-ranked tasks have opponent `-10.969`, margin
`+136.969`, cover 11 maps/all families/both seats, and yield whole-policy margin `+17.121`
with map interval `[+1.619, +32.623]`. This is also post-selected and not actionable. It shows
why the untested safety/coverage frontier cannot be replaced by the 70-task interval alone.

### 2. D92 is strong but narrower than the restored verdict

D92 reports 898 opponent-crop target selections versus D89's incidental 166—a 5.4-times nominal
dose with the productive starter unchanged—yet opponent score moves `+0.188`, own score falls
`5.422`, and margin falls `5.609`. This is the strongest negative causal evidence in the record.

The D92 document itself interprets the trained worker as “too late or too low-leverage.” Target
selection is not proof of timely arrival, successful denial, or prevented harvest. D92 therefore
closes that exact trained-only ETA-6 target-order intervention. It strongly lowers the prior for
other denial schedules, but it cannot logically close every timing, capacity, or production-rate
repair.

### 3. One load-bearing curve is explicitly unmeasured

The original analysis labels the production-rate/conversion-timing curve U5 as unresolved. A
proportional-scaling calculation finds incompatible rates: the opponent gate asks for scale
`<= 0.0121`, while the margin gate asks for `>= 0.0504`. That is useful evidence only if benefits
and leakage scale approximately linearly. Concavity is the very unknown U5 would measure, so the
assumption cannot also prove U5 futile.

The bounded ring is negative evidence, not that missing curve: it changes geometry and extent,
and its own analysis says it does not directly throttle production rate.

### 4. “Missing and costly” is not “structurally impossible”

The pre-treatment snapshot needed for the proposed selector audit was never committed, so that
audit is not cheap and cannot run offline as first claimed. A new 512-row corpus or equivalent
measurement would be required. This is a valid cost reason not to continue. It is not evidence
that no learnable selector or throttle exists.

## What I concur with

I concur with the following substantive conclusions:

- D89a itself is rejected and unsafe.
- Its `+82.863` opponent-score increase and damaging Gold-adaptive interaction are real.
- D91's one selector grammar, D92's exact dual-value schedules, bounded-ring geometry, and the
  tested capacity/denial compositions are negative evidence and should not be retuned on the
  consumed maps.
- Raw zero D-1/D-4 compliance is mandatory; no repair can trade those failures for score.
- Route A's week of work and zero valid candidates does not make Route A the default winner.
- Neither route has evidence authorizing Phase 3, a value claim, or Arena action.

## Implication for the conditional-banana-farm design

This review does not approve or reject implementation. It changes how the design risk should be
described:

1. The design does not repair D89a's leak; it limits where and how long the farm is exposed.
2. Because the theft/own-production split is unresolved, the banana-bank abort may watch the
   dominant harm or a secondary symptom. Current evidence cannot tell which.
3. A total-outcome sensor is causally broader than a banana-only sensor, but choosing or tuning
   one requires a separately frozen behavioural/value protocol; this review does not authorize it.
4. Passing the design's behavioural gates would prove construction, not value. The D89a and D92
   evidence makes a later tail/value gate essential.

## Final disposition

**Dissent from `NOT_REPAIRABLE`. Use `UNRESOLVED`, strongly leaning `NOT_REPAIRABLE`.**

For project planning, “do not fund the missing measurement because the prior is poor and the
cost is high” is defensible. “The committed evidence proves structural impossibility” is not.
Evidence that would justify closing the verdict is a frozen, leakage-safe failure of the
pre-treatment conditional-activation question plus a controlled production-rate/timing curve,
or an equivalent argument that does not depend on linear scaling or a confidence bound being
treated as a ceiling.
