# D112a dense q6 counterfactual teacher — mechanics-only result

Date: 2026-07-22  
Decision: **collector/reproducibility pass; frozen support gate fail; value not interpreted**

## Execution and repair

D112a enumerates every eligible paired q6 proposal along 128 exact D40 tasks. The initial runner
emits 827 roots and 13,377 independent one-deviation continuations, but takes 1,285.85 seconds
(`10.403` arms/s), below the frozen 12 arms/s mechanics floor.

Repair 1 snapshots the exact environment and opponent state at each root instead of replaying the
same prefix for every arm. An excluded-map smoke matrix is byte-identical before and after repair,
and every opponent family passes a cloned-continuation equality test. Two repaired full runs take
645.31 and 640.65 seconds (`20.730` and `20.880` arms/s). Their arm and baseline matrices are
byte-identical to one another and to the slower pre-repair matrix. The repair is therefore a 1.99x
full-panel execution improvement with no semantic change.

## Mechanics and coverage

All prescribed 128 baselines exist. The 827 roots contain 4--27 proposals and the tasks contain
0--18 roots. All 13,377 arms have finite nonzero 379-value action differences, exact one-use
accounting, paired-gain error at most `6.0e-8`, reward identity error at most `2.3e-7`, and zero
direct-command, provenance, or deposit-prediction failures. Frozen inputs and all repeated bytes
match.

One prospective mechanics rule fails: six tasks expose no eligible paired q6 boundary, while the
protocol required at least one per task. These are legitimate control-only episodes, not missing
rows: four finish at turn 301 but never expose a paired proposal, and two resident games terminate
at turns 197/215 with one worker. The remaining 122 tasks are represented completely.

Because mechanics fails, the analyzer does not read score or paired-gain fields, produces no DP
labels, and does not compute oracle, family, signal, or safety metrics. The 13,377 continuation
outcomes remain uninterpreted.

## Conclusion

Close D112a on its frozen coverage definition; do not waive the gate or interpret its value. The
next iteration keeps the collector, value thresholds, one-use authority, and backward-DP rule but
changes the task semantics prospectively on fresh maps: a task with no q6 boundary is a valid
forced-control task with zero oracle gain and no arm labels. Require high panel support rather than
universal support, then analyze all tasks including the forced controls.

Result JSON: `4025860ee86f458659a07866a95795db572f2c8a1c361c758ce65d56fe14dd39`  
Repair manifest: `1fb71574d2fc94467c65587d55a07f1c305bfac0940d3a9b8ddf5c5416cc170c`  
Arm matrix: `d097ad835d8ec2253c89b1558f3b3fb97eb3b71e32a8d952a8f0cf3297810032`
