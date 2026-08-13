---
type: HANDOFF
task_id: 20260803-orchard-ablation-causal-audit
from: chatgpt_1
to: local_codex_1
cc: user
created_utc: 2026-08-03T18:46:00Z
requires_ack: true
---

# Handoff: checkpoint-level orchard postmortem complete

## Outputs

- mechanism/amplification report:
  `chatgpt_1/orchard-ablation-mechanism-and-amplification-2026-08-03.md`
  at commit `1918e1fe7262365b9ecccbba3c9bdb94ffbb6783`;
- reproducible checkpoint analyzer:
  `chatgpt_1/orchard_ablation_checkpoint_analysis.py`;
- opponent-standardized JSON/Markdown:
  `chatgpt_1/orchard-ablation-opponent-standardized-2026-08-03.*`
  at commit `84991ff9eb68e53d91caf74a5b71135ca1c0417e`.

## Main correction

The apparent 25.3/rank-12 to 23.27/rank-34 effect is mostly not source effect. Exact same-source
E7a resubmission reads 23.56/rank 32. Thus 1.74/2.03 = 85.7% of the score gap and 20/22 = 90.9%
of the rank gap reproduce with zero source change. The fresh source-consistent difference is only
+0.29 score and two places for orchard.

## Fresh comparison

- orchard: 162 games, 93W/3T/66L, mean margin +9.81, 18 catastrophes;
- no orchard: 160 games, 91W/4T/65L, mean margin +10.57, 16 catastrophes;
- 35 common exact opponents, opponent-set Jaccard 0.427;
- opponent-standardized outcome signs depend on weighting and cluster-bootstrap intervals include
  zero broadly.

## Mechanism disposition

The secure orchard is sparse and high-output. Prior live attribution finds orchard-scale reaping in
11/160 games with 1,168 fruit. Controlled task-market release on 99 seed-repaid active cells loses
61.354 margin because +4.687 wood cannot replace 81.727 lost own-crop APPLE; 92/99 cells regress.
The starter is a saturated producer, not idle labor.

## Ranked implementation lead

Preserve the mother and add a monotonic alternate-door banking commitment for worker 2 during active
orchard states. Next audit safely missed activations without lowering safety thresholds. Do not
repeat global release, broad early farm, species substitution, mother-tie tuning or broad renewable
loops.

## Requested addendum

The exact host replay join requested in the 18:31Z question remains useful. Please return activation
support, near-miss reasons, APPLE banked, starter reservation, worker-2 bank latency/liveness and any
paired same-map/opponent/seat support. No source or Arena action is requested.