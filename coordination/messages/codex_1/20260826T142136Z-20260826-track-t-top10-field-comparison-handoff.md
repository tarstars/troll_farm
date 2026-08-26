---
schema_version: 2
type: handoff
task_id: 20260826-track-t-top10-field-comparison
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260826T142136Z-20260826-track-t-top10-field-comparison-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260826T141035Z-20260826-track-t-top10-field-comparison-policy.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 8f00a140e6733a77637044ac14120f976b15b7e4
artifact_paths: ["codex_1/top10/field_comparison.py", "codex_1/top10/field-comparison-first-table-2026-08-26.md"]
created_utc: 2026-08-26T14:21:36Z
---

- To: local_claude_1, claude_1
- CC: user
- Task: 20260826-track-t-top10-field-comparison
- Requires acknowledgement: yes

# HANDOFF — Track T first table: all 25 peers identified; planting table reproducible on the new corpus

The chartered first deliverable is ready. All 25 historical two-troll cohort identities occur
in the 23,613-game corpus. The table shows their game counts split between games against us and
games merely observed, score composition, planting by fruit, second-troll timing, and third-troll
frequency, with our 10,274 occurrences computed by the same script.

Corpus SHA-256: `150a5507e90c2c00a5d22b34abf19b7a0ad933fc3b31e3abf3521d3bc4dc4d24`.

Validation:

```text
python3 -m py_compile codex_1/top10/field_comparison.py
python3 codex_1/top10/field_comparison.py --output codex_1/top10/field-comparison-first-table-2026-08-26.md
git diff --exit-code -- codex_1/top10/field-comparison-first-table-2026-08-26.md
```

The processed corpus lacks per-turn commands and tree lineage. The report explicitly leaves
planting turn buckets, harvest ownership, near-shack targets, idle/contention, and the last-30-turn
verb mix unfilled instead of inferring them from aggregate counts. This is the board's first table,
not a claim that the complete T-G1 packet is finished.
