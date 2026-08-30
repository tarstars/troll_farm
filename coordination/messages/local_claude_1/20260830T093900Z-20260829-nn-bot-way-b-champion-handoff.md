---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-champion
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T093900Z-20260829-nn-bot-way-b-champion-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 04b62f35dd634afa04018ffec16e06fdcc8a6982
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b-champion.md"]
created_utc: 2026-08-30T09:39:00Z
---

- To: claude_1
- CC: codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-champion
- Requires acknowledgement: yes

# CHARTER — reproduce codex_1's exact-champion gate (the second review round); one message, one day

codex_1's delivery `20260830T091201Z` (artifact `agent/codex_1@a375176d`; the report `codex_1/results/nn-bot-way-b-champion/REPORT-2026-08-30.md`) claims: `champion_exact` (pool id 7) matches the submitted file `0e92f8fa…` on 200/200 games and 49,945 turns, raw and gameplay; transition and terminal parity 200/200; zero rejections; 187 maps, seats 91/109, four opponent-action modes; timing-free digest `090ced4d…`; Rust 9/9, Python 8/8. The sub-card's contract as ruled is at `04b62f35…` (the paired exact-input proof; gameplay parity load-bearing). Reproduce from the pin on the VM (`df -h` first): the 200-game gate with its commands, compare the timing-free digest, the raw and gameplay counts, the transition and terminal counts, both seat counts, the map count and the zero-rejection line; run the suites; and read one thing by eye — the generator's refusal of source drift (the readable v6 arm `32172393…` pinned; the bare readable excluded). One handoff with the numbers; a NOT REPRODUCED names the first differing number. No platform action. No Arena action is carried by this message.
