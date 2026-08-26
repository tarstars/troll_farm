---
schema_version: 2
type: update
task_id: 20260826-candidate-3b-stuck-holder-release
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260826T145820Z-20260826-candidate-3b-stuck-holder-release-update.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-26T14:58:20Z
---

- To: claude_1 (my own queue — this is the replacement card for what I am postponing)
- CC: local_claude_1 (board row D-4), codex_1, user
- Task: 20260826-candidate-3b-stuck-holder-release
- Requires acknowledgement: no — a self-addressed carry-forward, not a request

# DEFERRED: D-4 Candidate 3b — the build starts next session, and here is exactly where it starts

0-3a took this session's build time and is delivered. D-4 is postponed, not dropped, and it is not
blocked: D3-G1's accept condition was satisfied at `145051Z`, so the panel may be read when it is
run.

**First concrete step, no re-reading required.** Write the pre-commitments into
`coordination/tasks/20260826-candidate-3b-stuck-holder-release.md` before anything is generated
(containment; `xc = 0` on the six loop games; own-score outside `m061` ≥ +20; both `m061` seats
within 10 of the champion, 75 / 82; no Candidate-3-won game lost; `ka` max < 60; determinism; every
changed game named). Then extend `claude_1/cure3/make_cure3_source.py` with rule iii — a holder on
at most two cells for 20 turns with no work command releases, reason `rs=` — as one more anchored
replacement, keeping the one-source-one-flag-line shape so `build_arms3.py` still proves the arms
differ by a single line. Nothing else moves: no margin, no cap, no `dance20` widening.

**UNBLOCK-SIGNAL: none needed.** This is queued behind nothing; the next session picks it up first.
