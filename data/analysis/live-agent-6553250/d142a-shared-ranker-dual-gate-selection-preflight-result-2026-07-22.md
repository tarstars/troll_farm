# D142a shared-ranker dual-gate selection — preflight result

Date: 2026-07-22  
Decision: **repair calibration tie mechanics before any selection artifact**

D142a began under lock SHA `7dce6239...`. Completed workers reproduced both D140 and D141
component hashes exactly, confirming that one shared ranker plus the two separately trained gates is
semantically identical to the source models before averaging.

The run stopped after 3m08s with no selection artifact. The exact 50/50 float32 mean created equal
task-maximum logits across the requested training-count boundary. The inherited D125 scalar-offset
calibrator requires `active_floor > inactive_ceiling` and raised `gate quantile boundary is tied`.
No policy result, D126 score, checkpoint, fresh data, or platform action was produced.

This is a representation issue in the calibrator, not evidence about the dual-gate policy. Freeze a
mechanics-only D142b repair: order task maxima lexicographically by `(mean_logit,
stable_task_priority)`, use the Nth pair as the inclusive cutoff, and convert root decisions to
binary gate values before calling the unchanged policy evaluator. The stable priority matters only
when logits are exactly equal. It must hit the same frozen target count exactly and retain the exact
50/50 logits and component-hash guards.
