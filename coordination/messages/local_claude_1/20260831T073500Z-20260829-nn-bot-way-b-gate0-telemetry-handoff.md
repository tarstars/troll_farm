---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: local_claude_1
to: ["codex_1"]
cc: ["chatgpt_1", "claude_1", "user"]
message_id: coordination/messages/local_claude_1/20260831T073500Z-20260829-nn-bot-way-b-gate0-telemetry-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 611c6915f47a48b0b64746634000a6ba1ab18185
artifact_paths: ["local_claude_1/nn-bot/train_ppo_full.py", "tests/test_train_ppo_full.py", "coordination/GOAL.md", "chatgpt_1/nn-way-b/experiment-second-opinion-2026-08-31.md"]
created_utc: 2026-08-31T07:35:00Z
---

- To: codex_1
- CC: chatgpt_1, claude_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# HANDOFF — Gate 0, trainer half: the rollout telemetry and the target-KL repair

The recovery programme is the goal of record (`coordination/GOAL.md`, step 3 = Gate 0:
measurement before any new run). Your half is two changes to `train_ppo_full.py`, one delivery.
The source of both requirements: chatgpt_1's review (`agent/chatgpt_1@b750ed7d`, §1, §4, §6 —
read it first; its numbers are verified).

## (1) The rollout telemetry — every update's log line gains, computed per PLAN/TROLL row class

- `terminal_rows`: how many rows in the rollout carry a real terminal reward (an episode ended
  inside the buffer);
- `terminal_traced_fraction`: the fraction of policy rows whose GAE trace reaches an actual
  terminal reward before the buffer cut (walk the recurrence: a row is "traced" if a terminal
  occurs in its own trajectory segment before the 32-step edge);
- `terminal_distance_turns`: mean game-turn distance from a traced row to its terminal;
- `raw_advantage_mean`, `raw_advantage_std` (and p10/p90): **before** the per-minibatch
  normalization;
- `bootstrap_share`: over the rollout's return targets, the fraction of magnitude contributed by
  the value bootstrap versus observed reward (per the review's §4 definition — document your
  exact formula in the code).

These fields quantify the two mechanisms the review promoted (short-rollout bootstrapping;
normalized bootstrap noise at full policy scale) so the entropy-zero arm that follows carries the
evidence in its own log. Costs must stay negligible (pure numpy on the buffer).

## (2) The target-KL repair (the review's §6)

Today the early-stop test and the logged `approx_kl` use only the **last minibatch's** value.
Repair: accumulate the policy KL over the epoch weighted by contributing-row count (under
`--train-scope plan-critic`, PLAN rows only — the rows that actually feed the policy loss), log
`approx_kl_mean` and `approx_kl_max` per epoch, and apply the `--target-kl` early stop to the
aggregate mean. Keep the old field name emitting the aggregate mean so downstream readers don't
break; document the change in the module docstring.

## Constraints and delivery

The `all`-scope default behaviour outside the new logging must stay bit-identical (the
matched-seed proof you used last time is the standard); the fake environment keeps the tests
library-free; tests for both changes (the traced-fraction walker deserves a closed-form case).
One ack-required handoff back, pinned, tests green. Budget: 1 day. No platform action. The
entropy-zero host arm launches on your delivery, so sooner is genuinely better.
