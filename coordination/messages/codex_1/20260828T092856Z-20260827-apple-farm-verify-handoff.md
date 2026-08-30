---
schema_version: 2
type: handoff
task_id: 20260827-apple-farm-verify
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "user"]
message_id: coordination/messages/codex_1/20260828T092856Z-20260827-apple-farm-verify-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260827T134821Z-20260827-apple-farm-verify-blocker.md", "coordination/messages/local_claude_1/20260827T140222Z-20260827-apple-farm-verify-handoff.md"]
supersedes: ["coordination/messages/codex_1/20260827T181706Z-20260827-apple-farm-verify-handoff.md"]
artifact_ref: agent/codex_1
artifact_commit: 040470bc8dff19cfa0e5ab2482ac67f01eb9bef6
artifact_paths: ["local_claude_1/apple-farm/champion-apple-farm-v6-instrument.rs.sha256", "cgauto/submissions/candidate-apple-farm-v6-instrument.rs", "local_claude_1/apple-farm/results/fixtures.json", "local_claude_1/apple-farm/smoke-maps-seed0.jsonl", "local_claude_1/apple-farm/results/smoke.json", "readable/diffs/apple-farm.diff"]
created_utc: 2026-08-28T09:28:56Z
---

- To: local_claude_1
- CC: claude_1, user
- Task: 20260827-apple-farm-verify
- Requires acknowledgement: yes

# REDELIVERY — apple-farm reproduction after the orchard rebase

This discharges the apple-farm assignment and its self-addressed deferral after the orchard rebase made the previous delivery pin unreachable. The accepted technical verdict is unchanged: **REPRODUCED**.

- diagnostics arm SHA-256: `82c8ddd1347c8016aa80cdf883819e28ac867e7a193223f0c5311568d4833cf4`
- compacted submission SHA-256: `8c6bc206417c6d22b593372ce42e74ce5698646c1f8a860073f349a2a082708c` (66,082 bytes)
- bed: plays 34/34; differs 2/34; deterministic 34/34; compacted equals arm 34/34; telemetry errors 0
- smoke: mechanics pass 24/24; own-score sum arm minus resident +2831

Diff verdict: nothing in the insertion can make an own troll fell the farm tree or plant on the farm cell while the farm troll is away. This is transport repair only; no Arena action was taken.
