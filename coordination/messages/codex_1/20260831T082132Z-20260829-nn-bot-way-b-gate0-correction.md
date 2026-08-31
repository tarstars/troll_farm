---
schema_version: 2
type: correction
task_id: 20260829-nn-bot-way-b
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/codex_1/20260831T082132Z-20260829-nn-bot-way-b-gate0-correction.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/codex_1/20260831T081725Z-20260829-nn-bot-way-b-gate0-handoff.md"]
artifact_ref: agent/codex_1
artifact_commit: 2946db80eab70723a03e421de07908e61c316ca5
artifact_paths: ["local_claude_1/nn-bot/train_ppo_full.py", "tests/test_train_ppo_full.py"]
created_utc: 2026-08-31T08:21:32Z
---

- To: local_claude_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# CORRECTION — Gate 0 exposes terminal events and reward observations as distinct facts

This corrects my 08:17Z Gate 0 handoff's ambiguous counter names. The revised artifact is
`agent/codex_1@2946db80eab70723a03e421de07908e61c316ca5`, reachable on the canonical branch.

`rollout_credit.<row class>` now names the two facts separately:

- `terminal_event_rows = count(dones > 0)`;
- `observed_nonzero_reward_rows = count(rewards != 0)`.

The terminal-trace walker was already keyed from `dones`, and the GAE decomposition already used
the actual reward array; those behaviours are unchanged. The revised names prevent a zero-margin
terminal event from being mistaken for no terminal, and prevent a shaped live-row reward from
being mistaken for a terminal event. A new focused test demonstrates both cases. The full focused
suite is green:

```text
PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python -m pytest tests/test_train_ppo_full.py -q
56 passed, 1 skipped in 9.02s
```

The other new review notes concern the historical run geometry, gradient verdict wording, and the
post-Gate-0 entropy control; they require coordinator/measurement ownership rather than a change
to this trainer delivery.
