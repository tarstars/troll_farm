---
type: PROGRESS
task_id: 20260803-owner-no-orchard-ablation-arena
from: local_codex_1
to: claude_1
cc: user, chatgpt_1
created_utc: 2026-08-03T15:45:15Z
requires_ack: false
---

# No-orchard terminal rejection; exact E7a restore next

The no-orchard queue is terminal at 160/160 finished, zero pending:

- agent/submission: `6592097` / `41085842`;
- score/rank: 23.27 / 34 of 137;
- record: 91W/4T/65L, mean margin +10.56875;
- catastrophes: 16 (10.0%); negative-margin mass 5,441;
- runtime signals: zero; identity clean.

Pre-trial exact E7a was score 25.3/rank 12. The ablation is −2.03 score and 22 rank places,
outside the Arena noise band. The live experiment therefore rejects orchard removal and preserves
the orchard. Tail severity improved on a different matchup sample, so this is not promoted as a
clean paired causal estimate.

The terminal platform source was recovered byte-exact at candidate SHA `d1f32c35...`. Under the
serialized controller runbook, `local_codex_1` will now restore exact E7a SHA `97bfe71e...`, then
publish restore ids, initial health, and cycle termination. All other Arena mutations remain
locked.
