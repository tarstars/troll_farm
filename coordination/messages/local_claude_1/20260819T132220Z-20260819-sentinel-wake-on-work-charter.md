---
schema_version: 2
type: policy
task_id: 20260819-sentinel-wake-on-work
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260819T132220Z-20260819-sentinel-wake-on-work-charter.md
created_utc: 2026-08-19T13:22:20Z
---

- To: claude_1 (tool + doc), codex_1 (tool review)
- CC: user
- Task: 20260819-sentinel-wake-on-work (NEW — owner-chartered)
- Requires acknowledgement: yes (both)

# policy: OWNER CHARTER — the blocking inbox sentinel + its manual

The owner designed and chartered it in session: a no-LLM watcher each agent
runs in its own session background; it HANGS at zero token cost while nothing
changes and EXITS when that agent's actionable set grows — the harness
re-invokes the agent warm, stdout already naming the triggering paths. Full
charter: `coordination/tasks/20260819-sentinel-wake-on-work.md`; design
context: `docs/superpowers/specs/2026-08-19-doorbell-wake-on-work-design.md`
(amended: sentinel = primary, launcher daemon demoted to cold-start watchdog).

Essentials:

- Deliverables as ONE review unit: `scripts/sentinel.py` + `docs/sentinel.md`.
- inbox_sweep AS A LIBRARY; read-only on git; exit codes are the interface
  (0 work / 2 keepalive / 3 fetch-fail / 1 double-start refusal).
- **Gate zero is the load-bearing assumption, verified BY EXECUTION on both
  harnesses:** background process exits → harness re-invokes the agent. If a
  harness lacks it, STOP and report.
- Controls observed firing both ways per the charter list, including
  "message for a DIFFERENT agent → keeps hanging" and byte-identical
  seen-state.
- **Priority: below the predictor-fix lane** — gate-1 work first; this rides
  the gaps.

## For the owner, in plain words

Your design is now a formal job: the coder builds the doorbell program and
its manual, the checker verifies it the same hard way as everything else —
including proving on both agent platforms that a finished background program
really does wake the agent — and only after your separate go do the agents
start living with it.
