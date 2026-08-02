---
type: HANDOFF
task_id: 20260802-banana-ring-b100-successor
from: local_codex_1
to: chatgpt_1
cc: claude_1, user
created_utc: 2026-08-02T17:28:00Z
requires_ack: false
---

# Bounded banana-ring successor is SMOKE_QUALIFIED for owner-directed publication

The owner-corrected successor is mechanically ready and smoke-qualified. The sole Arena artifact
is `local_codex_1/banana-ring-b100-successor/banana-ring-b100-e6.arena.rs`, 99,990 bytes,
SHA-256 `d2d8f65804991fed5ca8cdaacc1b62fd90ab553ee6952c6286029497e525eecc`.

Final gates:

- 39/39 semantic tests;
- 8/8 full-vs-Arena streams, 2,400 exact command lines;
- optimized compile, mutated-parent rejection, empty-input and runtime stderr clean;
- p95 1.727 ms, maximum 5.402 ms;
- no outside-ring plants, no full-ring PICK, positive full-ring DROP and orthogonal chop/wood;
- zero ordinary diagonal chops after the r4 starter-fallback defect was fixed;
- paired smoke severe-tail gate passes.

Exact fallback remains the 64,522-byte b100/e6 source at SHA-256
`6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19`.

The owner explicitly directed publication. Local will push this exact packet, re-read platform
identity/fallback and concurrent-cycle state, and submit once as sole controller. No peer should
mutate Arena.
