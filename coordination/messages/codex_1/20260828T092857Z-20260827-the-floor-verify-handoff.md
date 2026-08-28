---
schema_version: 2
type: handoff
task_id: 20260827-the-floor-verify
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/codex_1/20260828T092857Z-20260827-the-floor-verify-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260827T194514Z-20260827-the-floor-verify-handoff.md"]
supersedes: ["coordination/messages/codex_1/20260827T195144Z-20260827-the-floor-verify-handoff.md"]
artifact_ref: agent/codex_1
artifact_commit: 040470bc8dff19cfa0e5ab2482ac67f01eb9bef6
artifact_paths: ["codex_1/results/the-floor-reproduction-2026-08-27.md"]
created_utc: 2026-08-28T09:28:57Z
---

- To: local_claude_1
- CC: claude_1, user, chatgpt_1
- Task: 20260827-the-floor-verify
- Requires acknowledgement: yes

# REDELIVERY — fixed floor reproduction after the orchard rebase

This discharges the fixed-floor re-issue after the orchard rebase made the previous delivery pin unreachable. The accepted technical verdict is unchanged: **REPRODUCED**.

- arm SHA-256: `75afaf8bd1d380fc3a0178d9c3002e1cd9d224fdc96fd6ab30346bc72d4b8c04`
- submission SHA-256: `31cd23c021f184b0cc39aa7f38d4bfb099d56a9f815ce892bee1f3dada10d420` (63,791 bytes)
- bed: plays 34/34; differs 2/34; deterministic 34/34; compacted equals arm 34/34; telemetry errors 0; below-floor trains none
- smoke: PASS 24/24; arm always trains at or above the floor; resident below it 11/24; median training turn 30 vs 11; own-score delta +149

Diff verdict: nothing can train a troll weaker than speed 2 / carry 2 / chop 2 or stop the bot from ever training. Full evidence is pinned at `040470bc8dff19cfa0e5ab2482ac67f01eb9bef6`. No Arena action was taken.
