---
schema_version: 2
type: handoff
task_id: 20260904-champion-prefix-orchard
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/chatgpt_1/20260904T144000Z-20260904-champion-prefix-orchard-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260904T133200Z-20260904-champion-prefix-orchard-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 2fc4d285c391b66fc575ae2fec00d0957ea3c9e2
artifact_paths: ["chatgpt_1/champion-prefix-orchard/FINAL.md", "chatgpt_1/champion-prefix-orchard/RESULTS.md", "chatgpt_1/champion-prefix-orchard/results/result.json", "chatgpt_1/champion-prefix-orchard/oracle.py", "chatgpt_1/champion-prefix-orchard/policies.json", "chatgpt_1/champion-prefix-orchard/action-vocabulary.json", "coordination/status/chatgpt_1.md", "coordination/BOARD.md"]
created_utc: 2026-09-04T14:40:00Z
---

# HANDOFF — champion-prefix orchard is dead on normal paired replay

The owner-authorized experiment is complete at the artifact pin. The unchanged champion was the executable in both arms and every candidate command stream was byte-identical through the champion's own second `TRAIN`; the second troll's specification and turn never changed. Third training was disabled and `NO_PLANT` was legal.

After correcting a tested planter self-occupancy instrument bug without changing the frozen grid or thresholds, the oracle evaluated 20 planting policies over 24 development map-seats plus cached champion baselines. Seventeen planting policies introduced a new long-inactivity interval and were excluded. The three globally valid planting policies all had negative mean paired final margin. The registered leave-one-map-out selector chose `NO_PLANT` in all 24 folds:

```text
Δ final margin: 0.00, 95% bootstrap interval [0.00, 0.00], n=24
Δ own score:    0.00, 95% bootstrap interval [0.00, 0.00], n=24
```

This triggers dead condition 3. High raid, panel, holdout and ladder stages were not run. A hindsight per-map oracle chose an orchard on 16/24 maps, but that is an optimistic upper bound selected from the same final outcomes, not a policy; the pre-registered cross-map selector could not generalize it.

**Recommendation: close row 3-8, no ladder slot, no parameter or map-selector tuning on this development set.** Per the card, please charter `claude_1` to reproduce the measurement independently without reading this implementation. The detailed fixed-policy decomposition, hindsight upper bound, calibration warning and reproduction command are in `FINAL.md`.
