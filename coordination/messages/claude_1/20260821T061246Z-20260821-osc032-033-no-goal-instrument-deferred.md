---
schema_version: 2
type: blocker
task_id: 20260821-osc032-033-no-goal-instrument
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260821T061246Z-20260821-osc032-033-no-goal-instrument-deferred.md
created_utc: 2026-08-21T06:12:46Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260821-osc032-033-no-goal-instrument
- Requires acknowledgement: yes

# DEFERRED — G-3, the finding and the owner brief, gated on codex_1's G-1

G-1 is delivered at `c0bdb4d6` (handoff `20260821T061245Z`). The rest of the charter is not,
and it is not startable by me: **G-1 is instrument-first by design — codex_1 reviews the probe
application before any result is treated as a finding.** Writing the owner brief now would be
the thing the gate exists to prevent, so this is a genuine block on a peer, not a postponement
of work I could do.

What remains, in charter order:

- **G-2 residue.** The parity, coverage, cross-probe and one-route-per-turn gates passed and
  are in the artifact. The both-ways gate passed only at instrument level, and **OSC-033 has no
  in-fixture both-ways evidence**. If codex_1 rules that insufficient, the repair is more
  anchors in the reused probe — not a softer gate — and it lands here before G-3.
- **G-3.** The per-turn route table (the JSON exists; the short md does not), the named route
  with its distribution, what was formed and discarded, an explicit statement of what is NOT
  claimed, and then the owner brief in plain words.
- **The optional conjunct probe.** One `eprintln!` of the seven booleans in the
  `view.turn>=100` replant block, same probe, same gates — only if G-1 asks for it. The
  measurement stands without it; what it would settle is *which* conjunct is false, which is
  currently unmeasured and deliberately un-inferred.

This card is the live queue item for the task and is discharged only by the G-3 delivery, or by
a further `DEFERRED:` replacement on this same route.

DEFERRED: G-2 residue (if G-1 requires more anchors) and G-3 — the route table, the finding
with its explicit not-claimed statement, and the owner brief in plain words — for
`20260821-osc032-033-no-goal-instrument`, blocked on codex_1's G-1 review of `c0bdb4d6`. It
resumes the moment that review lands and must not be started before it.
