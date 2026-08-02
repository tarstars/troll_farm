---
type: HANDOFF
task_id: 20260802-banana-ring-b100-successor
from: chatgpt_1
to: local_codex_1
cc: claude_1, user
created_utc: 2026-08-02T16:33:00Z
requires_ack: true
---

# Owner-corrected bounded banana-ring successor; reuse the accepted fast publication lane

The owner inspected live full-factory agent `6590083` / submission `41081195` and reported the
actual defects: the plantation is too large to cut, bananas are not deposited in the tent,
placement must follow the existing gate/front-door logic, orthogonal neighbors are wood trees,
and diagonal neighbors are seed mothers.

I checked the just-completed publication preparation. We do not need new packaging machinery. The
accepted route already provides exact-parent generation, the factory-aware slimmer, 23 semantic
tests, optimized compile, eight-stream/2,400-command research-vs-Arena equality, stderr/latency,
source-size, sidecars, fallback recovery, and controller submission. The earlier general slimmer
was correctly rejected on 8/8 stream divergence; clone only the accepted factory-aware route.

Published successor packet on `agent/chatgpt_1-banana-ring-successor`:

- `chatgpt_1/banana-ring-b100-successor/protocol.md`;
- `chatgpt_1/banana-ring-b100-successor/implementation-delta.md`;
- `chatgpt_1/banana-ring-b100-successor/lock.json`;
- `coordination/tasks/20260802-banana-ring-b100-successor.md`.

The implementation delta is method-bounded: gate-aware ring helpers plus replacements for
plant-cell, reserve, harvest target, starter command, wood command and factory wrapper, with one
post-DROP state reconciliation. It reuses `ringfarm.rs` and `ringfix3.rs` as the expected-behavior
source and adds the missing full-ring surplus-DROP assertion.

Please acknowledge one of:

1. accept and transfer the proposed local build paths to `local_codex_1`;
2. assign another implementation owner and explicit non-overlapping paths; or
3. reject/narrow the successor before source generation.

No contributor Arena mutation is requested. The current live observation remains controller-owned
and read-only until you explicitly end or supersede its monitoring window.