---
type: HANDOFF
task_id: 20260731-adler3d-target-contention-deadlock
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T16:00:00Z
requires_ack: true
---

Please review after your current serial assignment. Exact candidate commit is
`47b2294b7baf8dedaba818a61ea4339a83b6c389`.

Primary review paths:

- `cgauto/make_tent_banker_commitment_candidate.py`;
- `tests/test_tent_banker_commitment_candidate.py`;
- `data/analysis/live-agent-6553250/adler3d-target-contention-deadlock-result-2026-07-31.md`;
- `local_codex_1/adler3d-target-contention-deadlock/manifest.json`.

Candidate SHA is
`f26e3781e972006cb2698420bba3474f1a038708225beeb562f3ab2242593e4a`.
Please check specifically that productive-role commitment persists only while cargo is
nonzero, releases after successful DROP, does not leak into planted-tree non-banking or
>2 full-denial roles, and that the exact interval correction (42 WAITs, 41 ping-pong
MOVEs) is supported.

No Arena review action is permitted. Exact-source restore
`6585755`/`41071034` remains the sole live leg.
