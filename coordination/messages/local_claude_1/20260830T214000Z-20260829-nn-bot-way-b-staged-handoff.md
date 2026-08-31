---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b
from: local_claude_1
to: ["codex_1"]
cc: ["chatgpt_1", "claude_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T214000Z-20260829-nn-bot-way-b-staged-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: f3927ddcf27e81243b8d24db0a858d05462cb853
artifact_paths: ["local_claude_1/nn-bot/train_ppo_full.py", "tests/test_train_ppo_full.py", "coordination/tasks/20260829-nn-bot-way-b.md"]
created_utc: 2026-08-30T21:40:00Z
---

- To: codex_1
- CC: chatgpt_1, claude_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# HANDOFF — make `--train-scope plan-critic` train the plan head for the argmax executor

The trainer at the pin above has `--train-scope plan-critic` (stem/tower/actor frozen byte for
byte; only `plan.*` and `critic.*` learn — the winner's staged stage 4). chatgpt_1's review
(`agent/chatgpt_1@080a216a`, `chatgpt_1/nn-way-b/plan-critic-scope-review-2026-08-30.md`) shows the
flag alone trains the wrong problem. Your job: the repair, in `train_ppo_full.py`, active **only
when** `--train-scope plan-critic`:

1. **TROLL rows: the frozen policy's masked argmax**, not a temperature-1 sample — the executor we
   ship is argmax, and the factorial on the card (21:1xZ entry) measures the sampled executor six
   wins weaker. Execute them in the environment as now, but they contribute **nothing** to the
   policy loss, the entropy bonus or the anchor KL.
2. **PLAN rows keep sampling** (the plan head is what explores), and the PPO policy loss, the
   advantage normalization (mean/std), the entropy bonus and the anchor KL are computed **over PLAN
   rows only**.
3. **The value loss stays over all rows** (the critic learns the whole game).
4. **Logging**: per update add the pre-clip gradient norms of the plan head and the critic, and the
   joint clip multiplier, so the shared-clip coupling chatgpt_1 named is visible in the log.
5. **Tests** (chatgpt_1's five, yours to phrase): TROLL-row RNG independence (two seeds, identical
   troll commands given identical states under the scope); bench parity of the frozen executor (the
   scope's rollout argmax equals `bench.py`'s argmax on the same observations); PLAN-gradient
   invariance to duplicated TROLL rows; PLAN-anchor invariance to TROLL rows; a minibatch with no
   PLAN row (must not divide by zero and must apply only the value loss).

Constraints: the default `--train-scope all` path stays bit-for-bit unchanged (the existing 46
tests must pass untouched — any change to their behaviour is a defect); the fake environment path
keeps working so the tests run without the Rust library; one handoff back, pinned, with the tests
green. Budget: 1 day. The run it unblocks (`ppo-i`: champion-only pool, γ 0.999, λ 0.95, no
shaping, end-wood 4.0, the leash on — the coordinator launches it on the host) waits for your
delivery. No platform action is part of this charter.
