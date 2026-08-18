---
schema_version: 2
type: policy
task_id: 20260818-osc031-forecast-defect-fix
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260818T181016Z-20260818-osc031-defect-ruling-and-fix-charter.md
created_utc: 2026-08-18T18:10:16Z
---

- To: claude_1 (Phase-1 probe owner), codex_1 (instrument-first reviewer)
- CC: user
- Task: 20260818-osc031-forecast-defect-fix (NEW — owner-chartered by ruling)
- Requires acknowledgement: yes (both — this opens both queues)

# policy: OWNER RULED "A DEFECT" — the forecast fix is chartered; Phase 1 is WHY

The owner ruled on the delivered brief at 15:36Z: the forecast's silent
"nothing there" is **a defect**. Ruling record:
`local_claude_1/adjudications/OSC-031-ruling-2026-08-18.md`. The 4c instrument
task is CLOSED with all gates passed; OSC-031 exits the 4b stamp list. Full
charter: `coordination/tasks/20260818-osc031-forecast-defect-fix.md` — read it
whole. The essentials:

- **Phase 1 (now): diagnose WHY** — a small parity-disciplined probe on the
  accepted 4c toolkit logging which internal exit of `predict_tree` produces
  `None`, per evaluation, over the pinned 167 turns. UNPRIVILEGED logging of
  every internal exit — same discipline that served 4c. Deliverable: mechanism
  note + a fix design PROPOSAL to the owner. **No fix code in Phase 1.**
- **Owner design gate between phases** — the fix touches planner core;
  two-correct-doors-make-a-wall is the standing hazard. The owner sees WHY and
  approves the door before anything is built.
- **Phase 2 (after the go): the fix**, fail-first gates as chartered (fixtures
  observed-failing → green, zero de-novo by turn coverage; 240-game panel vs
  matched floor; latency + parity; codex_1 reproduction). END STATE =
  ready-with-gates. **Submission is NOT in this task** — the cure-C night owns
  the Arena and a new candidate is a separate owner decision after it settles.
- codex_1: instrument-first on the probe, as ever. Nothing here preempts the
  night bookkeeping.

## For the owner, in plain words

Your ruling is recorded and the repair is now real work with the same
discipline that measured the problem: first the coder makes the forecast step
say WHY it answers "nothing there" (measured, not guessed), then you approve
the repair design, then it gets built and tested — and putting it on the
platform will be your separate call after tonight's experiment finishes.
