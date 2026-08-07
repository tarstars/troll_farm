---
type: PROGRESS
task_id: 20260803-orchard-ab-night-cycle
from: local_codex_1
to: user
cc: claude_1, chatgpt_1
created_utc: 2026-08-03T19:07:37Z
requires_ack: false
---

# Eight-leg orchard/no-orchard night cycle prepared

The sole Arena controller has prepared the owner's requested `N→O` ×4 schedule: four exact
no-orchard submissions, four exact orchard submissions, one hour per leg, ending with orchard.
Every leg will publish IDs, a clean checkpoint, complete sanitized replays, and hashes before the
next mutation. T+15/T+30/T+45 phase markers will be pushed automatically.

The submitter calls canonical `TestSession/submit` exactly once and has no endpoint fallback or
automatic retry. A 05:14–05:31 local network blackout protects the 05:17 daily collector. No
platform mutation has occurred at this preparation checkpoint.
