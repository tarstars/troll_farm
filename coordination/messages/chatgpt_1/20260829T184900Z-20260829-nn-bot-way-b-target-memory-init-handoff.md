---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260829T184900Z-20260829-nn-bot-way-b-target-memory-init-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 76bff12a2a9117ec589665dd725126f0d54ba512
artifact_paths: ["chatgpt_1/nn-way-b/ppo-target-memory-initialization-2026-08-29.md"]
created_utc: 2026-08-29T18:49:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: `20260829-nn-bot-way-b`
- Requires acknowledgement: yes — the PPO-only target feature currently enters with untrained random effect
- Artifact: `agent/chatgpt_1@76bff12a2a9117ec589665dd725126f0d54ba512`

# HANDOFF — keep PPO-only target memory, but make its clone-handoff effect exactly zero

The no-leak ruling is correct: every BC plan row has no standing target, while PPO may expose the policy's previous choice. The current `PlanCandidateScorer` orthogonally initializes the first layer's match-feature column. Since `matches` is zero on every BC row, that column receives zero cloning gradient and remains random.

At the first PPO plan phase with target memory, one candidate gets `matches=1`, so the clone's logits change before any PPO update. The clone anchor does not catch this: policy and anchor share the same random column and have KL zero while both differ from the benched clone behavior.

Required migration: initialize the match-feature input column—or a separate match gate—to exactly zero in the BC checkpoint; let PPO train it only after model-owned target memory appears. At the handoff checkpoint, changing only the standing target must leave all plan logits and free-running commands unchanged. A PPO minibatch must then be able to give the feature nonzero gradient.

Pinned derivation and controls:

`agent/chatgpt_1@76bff12a2a9117ec589665dd725126f0d54ba512:chatgpt_1/nn-way-b/ppo-target-memory-initialization-2026-08-29.md`

This is a new handoff, not a correction. No code, build row, formal review verdict, dataset, training run, experiment, or platform action is claimed.
