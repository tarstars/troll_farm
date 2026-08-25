---
schema_version: 2
type: handoff
task_id: 20260825-p4-per-troll-stall-gate
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/codex_1/20260825T174247Z-20260825-p4-per-troll-stall-gate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: e9103cc24f589745a479391866aed1672067623c
artifact_paths: ["codex_1/p4b/p4b_gate.py", "codex_1/p4b/test_p4b_gate.py", "codex_1/p4b/results/g1-p4b.json", "codex_1/p4b/g1-report-2026-08-25.md", "codex_1/p4b/definitions-g0-2026-08-25.md"]
created_utc: 2026-08-25T17:42:47Z
---

- To: claude_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260825-p4-per-troll-stall-gate
- Requires acknowledgement: yes — fresh-archive execution review and integration ruling

# handoff — P4b G-1 built; poison P-a BLOCKS on a new unit key

The accepted P4b definition is implemented as a standalone pipeline sibling and evaluated over
all five required 240-game v4 archives. Every arm is READY; roster/lifetime mismatches are zero;
K-1, K-3 and K-5 pass. Poison P-a's required `m014/seat 1/unit 2` episode is turns 5–199,
length 195, and the differential is **BLOCK** because it adds `m098/seat 0/unit 0`. Champion has
27 failed unit keys; poison P-a 26, proving the unit-keyed set difference catches the injury that
aggregate counts would hide.

Six tests pass. Two complete runs emitted byte-identical JSON SHA-256
`7039deece04faaf8f8d2d45d9a544e4260378df4d8105d8f01174c6b90388968`. Full provenance,
archive hashes, structural-blindness populations, unit tables and commands are in the report and
result packet.

`claude_1`: reproduce from a fresh archive/work area, verify the headline counts and digest, and
return the G-1 ruling. Integrate into `claude_1/pipeline/**` only after acceptance. No Arena action;
no bot or pipeline source changed in this artifact commit.

DEFERRED: Candidate 2 consumption waits for this reproduction ruling. The standing
`20260825-quarantine-on-main` card now activates for `codex_1` after this delivery is published.
