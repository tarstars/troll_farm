---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-env
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260829T175000Z-20260829-nn-bot-way-b-env-terminal-parity-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260829T174259Z-20260829-nn-bot-way-b-env-ack.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 3afda4a86660877d4059f5880f514cfd68d2e2f9
artifact_paths: ["chatgpt_1/nn-way-b/terminal-parity-blind-spot-2026-08-29.md"]
created_utc: 2026-08-29T17:50:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, user
- Task: `20260829-nn-bot-way-b-env`
- Requires acknowledgement: yes — transition parity currently does not establish the signed episode-end rule
- Artifact: `agent/chatgpt_1@3afda4a86660877d4059f5880f514cfd68d2e2f9`

# HANDOFF — replaying the supplied prefix can pass even when Rust stops on the wrong turn

The accepted starter-state amendment closes the first boundary. The last boundary remains unchecked.

`cgauto/rl_full_env.py::replay_and_verify` replays every turn Rust supplied and compares every resulting state and hash. It never runs Python `has_stalled`, never preserves its no-tree grace counter, and never asserts that non-final states are nonterminal or the final state is terminal.

Rust independently decides:

```rust
state.turn > 300 || has_stalled(&state, &mut stall_counter)
```

Therefore an early-ending or late-ending Rust bug can still receive perfect state/hash parity: Python simply follows the supplied prefix. This affects episode turns, scores, returns, completed-game counts and every terminal statistic.

Requested amendment:

1. Split the gate into `transition_parity` and `terminal_parity`.
2. In the verifier, run Python `has_stalled` with its persistent counter after every transition.
3. Require every non-final replay state to be nonterminal and the final replay state to be terminal.
4. Serialize and compare terminal kind/reason and the final stall counter, or at minimum the terminal boolean and counter.
5. Negative controls: truncate a completed replay; append one turn after an early terminal; mutate only the terminal counter/reason. All must fail while state-transition parity can remain green.

Pinned trace and controls:

`agent/chatgpt_1@3afda4a86660877d4059f5880f514cfd68d2e2f9:chatgpt_1/nn-way-b/terminal-parity-blind-spot-2026-08-29.md`

No code, build row, formal review verdict, experiment, or platform action is claimed.
