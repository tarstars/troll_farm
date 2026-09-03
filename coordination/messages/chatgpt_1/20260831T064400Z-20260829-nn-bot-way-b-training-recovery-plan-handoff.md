---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260831T064400Z-20260829-nn-bot-way-b-training-recovery-plan-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 018ab8c0a0d20886002397e0a4dda36e21048971
artifact_paths: ["chatgpt_1/nn-way-b/self-play-training-recovery-review-and-staged-plan-2026-08-31.md"]
created_utc: 2026-08-31T06:44:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# HANDOFF — self-play training recovery review and gated staged plan

At the owner's request, I converted the adversarial experiment review into an executable recovery programme. The pinned artifact contains the diagnosis, the required design changes, explicit budgets and a measurable `PASS` / `FAIL` / `INCONCLUSIVE` gate at the end of every stage.

## Core decision

Do not resume broad full-parameter PPO. The plan separates two failures:

1. full-model PPO rapidly corrupts the cloned executor through short-rollout, bootstrap-heavy normalized updates and the shared value-gradient path;
2. with the executor frozen, the plan head drifts more slowly under turn-by-turn target reselection, stochastic PLAN behaviour, entropy, weak outcome credit and overly broad action support.

The proposed sequence is:

```text
0 measurement/reproducibility gate
1 matched entropy-zero falsifier
2 persistent PlanOption + event-level supervised clone
3 complete-episode PLAN trainer + isolated critic
4 first honest plan-only RL pilot
5 three-seed replication
6 optional constrained executor fine-tune
7 existing 400+400 promotion and export gate
```

## Load-bearing gate rules

- 48 cells are scout-only; 192 untouched cells confirm; 400+400 remains promotion.
- Candidate comparisons use paired per-cell score-margin deltas and paired bootstrap intervals.
- The executor stays byte-frozen through Gate 5.
- PLAN policy credit in Stage 3 comes from completed episodes, with zero rollout bootstrap.
- A value-only step must produce zero policy-logit shift before gameplay training.
- Fixed teacher replay protects both plan and, later, command behaviour.
- Full trunk unfreezing is never one step; Stage 6 is optional and reversible.

## Requested coordinator action

1. Record this as the recovery design for Phase 3 rather than launching another undifferentiated PPO arm.
2. Charter Gate 0 first: corrected gradient instrument, raw-advantage/bootstrap telemetry, deterministic clone rerun, and locked evaluation populations.
3. Keep current cluster outputs as exploratory evidence; do not let them bypass the gates.
4. Charter the Stage-1 entropy-zero arm only after Gate 0 passes.
5. Assign Stage-2/3 implementation separately so persistent plan semantics and complete-episode credit are independently reviewable.

The artifact also defines exact stop rules and the final local/export gate. No trainer, checkpoint, run, YT operation, dataset, platform, ladder, leaderboard or Arena state was changed.
