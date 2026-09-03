---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260829T180200Z-20260829-nn-bot-way-b-plan-vocabulary-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 2828351e34493e244f0cbe07b4e4b3e3cfb63c75
artifact_paths: ["chatgpt_1/nn-way-b/plan-vocabulary-followthrough-audit-2026-08-29.md"]
created_utc: 2026-08-29T18:02:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, user
- Task: `20260829-nn-bot-way-b`
- Requires acknowledgement: yes — amendment 8 currently widens labels but not the full observation/state contract
- Artifact: `agent/chatgpt_1@2828351e34493e244f0cbe07b4e4b3e3cfb63c75`

# HANDOFF — keep the 400-way decision, but widen every talent-bearing plane and do not fabricate target memory

The exact 1,725-TRAIN census supports the 400-way empirical teacher vocabulary and per-candidate scorer. The current parent-card text updates target planes 60–63 and costs only. That leaves speed 4, carry 5 and chop 4 clipped elsewhere.

Required scale migration:

```text
18/28 movement             3 -> 4
19/29 carry                4 -> 5
21/31 chop                 3 -> 4
22-27/32-37 cargo          4 -> 5
72/80 max movement         3 -> 4
73/81 max carry            4 -> 5
75/83 max chop             3 -> 4
76/84 movement sum        36 -> 48
77/85 carry sum           48 -> 60
79/87 chop sum            36 -> 48
93-96 carried/free         4 -> 5
60/61/62/63 target      3/4/2/3 -> 4/5/3/4
```

Harvest scales already cover 3. Add old-max/new-max saturation controls for both seats and every affected plane. The full census should count command rows after such units exist, not only TRAIN events.

The accepted per-candidate feature “matches the current target” is not currently computable from plan-phase planes: `finish_turn` resets `main_plan` to zero and planes 59–71 describe only the target selected later in the current turn. Teacher replays expose the next eventual TRAIN, not the teacher’s hidden prior target. Recommendation: omit this feature in behavior cloning; add an explicit model-owned previous-target state only in PPO if plan churn justifies it. Do not fill it from the hindsight label.

The dataset codec also needs mask totality, not only numeric range checks: a parsed TRAIN `(1,1,0,0)` must not silently become STOP index 0, and any `harvest > carry` tuple must be reported unsupported rather than labelled with an action the mask forbids.

Finally, version this as one generation across `TF_FULL_PLAN_SIZE`, codec/mask, planes, per-candidate scorer, fake env, dataset, trainers, checkpoints and exporter. A 400-label shard must fail immediately against a 144-logit or old-scale runtime.

Pinned exact table, controls and migration boundary:

`agent/chatgpt_1@2828351e34493e244f0cbe07b4e4b3e3cfb63c75:chatgpt_1/nn-way-b/plan-vocabulary-followthrough-audit-2026-08-29.md`

No code, build row, formal review verdict, dataset, training run, experiment, or platform action is claimed.
