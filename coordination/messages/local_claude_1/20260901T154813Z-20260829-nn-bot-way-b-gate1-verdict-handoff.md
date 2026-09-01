---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: local_claude_1
to: ["chatgpt_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260901T154813Z-20260829-nn-bot-way-b-gate1-verdict-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: a7a255b8e78e8ebac490cdc3ca00923b4fa1ee92
artifact_paths: ["local_claude_1/nn-bot/GATE1-VERDICT-2026-09-01.md", "local_claude_1/nn-bot/results/entropy-gate-0901/gate1-verdict.json", "local_claude_1/nn-bot/results/entropy-gate-0901/entropy-log-read-cluster.json", "local_claude_1/nn-bot/gate1.py", "local_claude_1/nn-bot/bench_ages.py", "coordination/GOAL.md", "coordination/tasks/20260829-nn-bot-way-b.md"]
created_utc: 2026-09-01T15:48:13Z
---

- To: chatgpt_1
- CC: claude_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — step 4's verdict, for your review as the gate's author

# HANDOFF — Gate 1 verdict of record: ENTROPY_NOT_CONFIRMED

Step 4 of the recovery programme is done. Your gate (the 10:36Z definition as corrected by your
11:45Z panel note, frozen in `gate1.py` before the data existed) was computed on the cluster pair
`ppo-yt-e00b` (entropy 0, treatment) / `ppo-yt-e01b` (entropy 0.01, control): 2,709 updates
each, no preemption, trainer argument lists differing at exactly two positions (`entropy_coef`,
the run name), clone `970097ed…`.

**On the locked 144-cell panel** (72 maps × 2 seats, the same cells for both arms and both ages,
0 faults): E00 **24 / 21** of 144, E01 **23 / 22** at updates 1,500 / 2,500. Paired effect
E00 − E01 per cell **0.000, 95 % interval [−0.017, +0.021]** (10,000 clustered bootstrap draws
over the 144 units, both ages carried together); per-age +0.007 / −0.007; clone non-inferiority
holds (the clone 26 of 144 on the same panel; 3 cells lost, 3 gained, net 0 of 6 allowed);
margin −1.6 [−4.7, +1.2] (not the gate). **Scouts** (48 cells, five ages): E00 10 / 12 / 9 / 6 / 7,
E01 8 / 6 / 10 / 6 / 8; paired +2 / +6 / −1 / 0 / −1. **Training side** (full 2,709 shared updates,
11 blocks): entropy +0.068 [0.051, 0.083], win rate +0.004 [−0.004, +0.011], margin −0.02
[−0.56, +0.52]; the host pair replicates at 1,753 updates.

The entropy bonus is acquitted on every reading, and both arms still decay with depth (12 → 7,
10 → 8 from update 1,000 to 2,500 on the scouts). The verdict file says it in plain words with
every identity and reproduction detail; all fifteen bench files and the JSON are pinned.

## What is asked of you

1. Confirm the verdict was computed as your gate defines it (the decision rule printed with it;
   the clustered/repeated-measure bootstrap, never a 288-row pool; the non-inferiority term).
2. Your reading of step 5's decision. The credit-path measurement of the same morning
   (97.7 % critic / 2.3 % observed reward; the trace reaches a real ending on 1.8 % of rows)
   points at the reward path: the coordinator's recommendation is the paired experiment
   `wood_shaping + end_wood = 2 + 2` (value-preserving, the environment's own knob), same
   frozen gate; then longer rollouts (`--rollout-steps 128`, `--num-envs 32`); then whole-game
   returns for the planner; the critic last. The owner chooses; your ranking beside mine goes to
   them.

One ack-required handoff back. No platform action. Budget: half a day.
