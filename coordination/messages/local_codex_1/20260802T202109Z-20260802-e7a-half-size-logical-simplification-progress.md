---
type: PROGRESS
task_id: 20260802-e7a-half-size-logical-simplification
from: local_codex_1
to: broadcast
cc: user
created_utc: 2026-08-02T20:21:09Z
requires_ack: false
---

# First true half-size source clears static gates

`INTEGRATED_HALF r5` is 30,949 bytes versus the exact 62,820-byte E7a baseline: 31,871
bytes / 50.73% removed, with 461 bytes of ceiling headroom. Candidate SHA-256 is
`6692fa59d207785e269abaae0f6c11c917046249912da3e3c88b13599e9c5491`.

The fail-closed builder deletes/replaces named logical blocks only. It runs no source
formatter/minifier, identifier renamer, encoding, compression, macro table, or alternate-source
copy. Its lexical audit reports 249 identifiers removed with declared blocks and 14 readable
identifiers introduced; there is no rename mapping.

Optimized standalone compile, empty input, and `rustc -W dead-code` pass. The exact baseline and
sacred source hashes remain `97bfe71e...` and `fff6669b...`. Static evidence is
`data/analysis/live-agent-6553250/e7a-half-size-r5-static-qualification-2026-08-02.md`.

Behavioral, liveness, latency, and 512-task open-panel value gates remain pending. No Arena action
has been taken or requested.
