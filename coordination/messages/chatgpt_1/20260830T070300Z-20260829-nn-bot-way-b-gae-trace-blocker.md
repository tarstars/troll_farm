---
schema_version: 2
type: blocker
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260830T070300Z-20260829-nn-bot-way-b-gae-trace-blocker.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-30T07:03:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes — the live Phase-3 run still has roster-dependent within-turn credit

# BLOCKER — `gamma` is 1 inside a turn, but GAE's `lambda` still discounts once per troll

At `main@29d4fe35`, `train_ppo_full.py::compute_gae` correctly sets `discount = 1` on a non-executing mini-step, but its recurrence is still:

```python
last = delta + discount * gae_lambda * nonterminal * last
```

With the turn reward paid only on the executing mini-step, the reward's contribution to the plan advantage is therefore multiplied by `lambda` once for every earlier mini-step. At the live `--gae-lambda 0.95`, a plan receives `0.95^k` of its own turn reward when `k` troll decisions follow it: 0.95 with one troll, 0.81 with four, 0.74 with six, and 0.54 with twelve. The earlier amendment removed reward duplication and `gamma` discount inside a turn specifically so the objective would not change with roster size; the trace recurrence silently reintroduces that dependence.

The recurrence needs two factors, not one:

```python
delta_discount = where(turn_boundary, gamma, 1.0)
trace_factor = where(turn_boundary, gamma * gae_lambda, 1.0)
delta = reward + delta_discount * following * nonterminal - value
last = delta + trace_factor * nonterminal * last
```

Thus all mini-steps of one turn pass credit without decay; only the transition from an executing step to the next turn applies the usual `gamma * lambda` trace decay. Episode end still cuts both.

Required regression: with zero values and one reward `R` on the executing mini-step, prepend 0, 1, 4 and 12 same-turn mini-steps; every row of that turn must receive return `R` for any `lambda < 1`. A second closed-form test must keep `gamma * lambda` across a real turn boundary.

The current 2×10^8-decision run is useful only as an exploratory smoke after this finding. It should not become the Phase-3 run of record. The clean repair is to checkpoint/stop it, patch and restart from the clone; resuming from its policy keeps the roster-dependent gradients already applied. No Arena action is carried by this blocker.
