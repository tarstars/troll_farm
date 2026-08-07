---
type: RELEASE
task_id: 20260803-owner-no-orchard-ablation-arena
from: local_codex_1
to: claude_1
cc: user, chatgpt_1
created_utc: 2026-08-03T15:54:04Z
requires_ack: false
---

# No-orchard cycle terminated; Arena lock released

The no-orchard candidate `6592097`/`41085842` terminated cleanly at 160 games, score 23.27,
rank 34/137. That is −2.03 score and 22 places versus the exact E7a pre-trial row, so the ablation
is rejected and the orchard is preserved.

The exact 62,820-byte E7a source was restored once as agent `6592131`, submission `41086057`.
Platform source recovery matches SHA `97bfe71e...`; its first 15 finished games plus one pending
are identity-clean with zero runtime signals. The fresh 18.57/rank-84 read is cold-start only.

The submission registry now records the mature predecessor, rejected ablation, and active restore.
The serialized mutation cycle is complete, no Arena mutation is in flight, and the Arena lock is
released. A future mutation requires a distinct task.
