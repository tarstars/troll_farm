# D158a group-robust recurrent q6 PPO — abort adjudication

Date: 2026-07-23  
Decision: **stop before a policy result; the baseline-relative admission gate is invalid for the
Legend-rank objective**

D158 was frozen to isolate the omitted D109 objective question. Four same-seed variants started
concurrently and reached the common scheduled telemetry boundary at update 6 / 7,200 transitions.
They used approximately five cores each, preserved 100% crop creation, had zero mechanical or raw
reward-identity failures, and produced distinct policies and group weights as intended.

Those partial training returns are deliberately uninterpreted. No fit reached its frozen budget,
no checkpoint/evaluation/result file was written, and all four processes were terminated with
exit code 130.

## Why the protocol was stopped

The post-launch baseline audit found that q6 falls back to D40, not the current Yamo/Orchard
resident. D102 measured D40 at **-48.396 mean margin versus the resident**. On a different panel,
D148's hindsight oracle gains `+37.103` from exact one use and another `+4.110` from its selected
second use, about `+41.213` over D40. The panels differ, so these values are not a paired bound;
they do establish that D158's development `+1` and confirmation `+2` gates are nowhere near a
resident-competitiveness test.

Finishing D158 could answer a narrow optimizer question but could still authorize a policy roughly
forty points below the program we already have. That is not a profitable use of the experiment
budget under the third-place goal.

## Correction

Close D158 without claiming that group-DRO succeeds or fails. Preserve the tested trainer and
objective machinery for a future exact-resident environment, but do not resume these processes,
open confirmation maps, or select from partial telemetry.

From now on every controller protocol must satisfy one of two conditions before launch:

1. exact Yamo/Orchard fallback with gains measured directly against that resident; or
2. a same-panel proof that a different fallback already closes the resident gap, followed by gates
   stated against the resident rather than the weaker internal control.

Reserved maps remain sealed. No YT operation, Arena interaction, submission, candidate, or resident
mutation occurred.

