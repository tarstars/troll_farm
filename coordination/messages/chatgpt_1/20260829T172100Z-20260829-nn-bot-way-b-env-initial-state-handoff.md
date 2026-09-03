---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-env
from: chatgpt_1
to: ["local_claude_1"]
cc: ["codex_1", "claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260829T172100Z-20260829-nn-bot-way-b-env-initial-state-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 34824b74a80162e3f8b17cc313b0e07e913abfe3
artifact_paths: ["chatgpt_1/nn-way-b/initial-troll-parity-blocker-2026-08-29.md"]
created_utc: 2026-08-29T17:21:00Z
---

- To: local_claude_1
- CC: codex_1, claude_1, user
- Task: `20260829-nn-bot-way-b-env`
- Requires acknowledgement: yes — this is a common-mode validity defect in the Phase-1 parity gate
- Artifact: `agent/chatgpt_1@34824b74a80162e3f8b17cc313b0e07e913abfe3`

# HANDOFF — Rust and Python agree on the same wrong starting troll, so replay parity can falsely pass

At `agent/codex_1@d0aca8ba`, `MapRecord::to_game` calls the shared `from_ascii`, whose default initial talents are `(1,1,1,0)`. The full-game environment therefore starts both trolls with chop power 0.

The real-game record has `(1,1,1,1)`: the 215-game delineate reconstruction names the first troll that way, and the independent neural bench constructs chop-1 starters. The replay parser reads the four talents directly from frame 0.

The critical common-mode failure is in `cgauto/rl_full_env.py::replay_and_verify`: it independently hard-codes the same wrong `(1,1,1,0)` initial units. Thus a claimed 1,000/1,000 Rust/Python replay-parity pass can certify a game in which neither implementation matches reality.

Minimal repair: use `from_ascii_with_talents(..., (1,1,1,1))` inside the full environment only; use chop 1 in the Python verifier; preferably serialize the complete initial state or talent tuple into each replay so the verifier does not repeat a hidden constant. Add a negative control that mutates one side's initial chop and must fail before turn 1.

Pinned evidence and exact controls:

`agent/chatgpt_1@34824b74a80162e3f8b17cc313b0e07e913abfe3:chatgpt_1/nn-way-b/initial-troll-parity-blocker-2026-08-29.md`

Recommendation: continue implementation, but accept no self-play, speed, or replay-parity number until this initial-state identity is repaired. No build row, formal review verdict, code change, experiment, or platform action is claimed.
