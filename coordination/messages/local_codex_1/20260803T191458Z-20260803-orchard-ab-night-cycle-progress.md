---
type: PROGRESS
task_id: 20260803-orchard-ab-night-cycle
from: local_codex_1
to: user
cc: claude_1, chatgpt_1
created_utc: 2026-08-03T19:14:58Z
requires_ack: false
---

# Night A/B preflight abort corrected

The first launch stopped before maturity because read-only source recovery searched for the
untracked session file in the isolated worktree. No-orchard submission `41086801` was active for
approximately 66 seconds and is not counted as an experiment leg. The declared one-call orchard
safety restore is `6592329`/`41086809`, recovered byte-exact at SHA `97bfe71e...`.

The verifier now receives the explicit controller credential path and allows up to five minutes
for read-only propagation. Six focused tests pass. The complete eight-leg `N→O` ×4 sequence will
restart only after this correction and the abort evidence are pushed and remotely verified.
