---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T180104Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T171729Z-20260825-dance-cure-candidate-2-swap-stop.md"]
supersedes: []
created_utc: 2026-08-25T18:01:04Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (replacement): the G-1 STOP is discharged — the two diagnoses are delivered — and the ruling-4 deferred control set is NOT started

This card replaces the self-addressed G-1 STOP card (`20260825T171729Z`), which it discharges by
`ack_for`. The STOP itself is answered by the coordinator's `20260825T173045Z`: the loop goes
to the owner, `m061` and the loop anatomy are diagnosed now, and everything not depending on the
ruling proceeds. **The two diagnoses are delivered** at
`coordination/messages/claude_1/20260825T180028Z-…-handoff.md` (`agent/claude_1@85c6647c`).
What remains open, and is deferred here, is ruling 4's control set.

## DEFERRED: not started this wake, in the coordinator's own order

1. **C-10** — A-1 realised cells: the referee actually executes the circular swap, checked on every
   exchange. *This is the assumption the whole design rests on and it is still unchecked; it is the
   first thing the next wake does.*
2. **C-11** — the `prev_cells` check.
3. **C-13** — determinism (same spec, same stream, twice).
4. **C-7** — the poison arm: C-5 and C-6 must fire loudly on it, or they are inert.
5. **C-8** — the positive-control fixture.
6. **C-16** — the R-B red half.
7. **The P3 read on the candidate arm.** Until it is read, **P3 is UNMEASURED, not passed**, and
   every table I publish says so. The instrument arm cannot answer it — its `MSG` diverges the
   stream at turn 1.
8. **The 11 reproduced dance fixtures with `progress_restored`.**
9. **C-12** — per-troll idle-with-work; **P4b** joins it once codex_1 delivers (G-0 accepted
   17:20Z).

None of these is blocked by the owner's loop ruling, so none of them is waiting on anything but my
next wake. Nothing in the set has been started, half-run, or partially recorded: there is no
scratch state to reconcile.

## Two things the next wake must carry, because they were found this wake and belong to other cards

- **The `idle_regeneration` fallback in `main_candidates` returns a fresh `vec![WAIT]` and
  discards `out`**, including regeneration `PICK`s worth 7500 that the clause above it just
  built. It is in the champion, it is the same defect I reported unanswered on 2026-08-21, and it
  is worth **75 points on `m061`**. It is **not mine to fix on this card** and I have not fixed
  it. It belongs to whoever owns the planner, and the owner should be told it exists before the
  `m061` number is used to judge Candidate 2.
- **P4's exhaustion calibration excuses a stall the arm itself caused** by felling the last tree.
  Carried into the `20260825-p4-per-troll-stall-gate` definitions ruling as an input, with the
  caveat that a per-troll "work was available" gate would also stay silent on `m061`.

## Standing constraints while this card is live

No lock, no timer, no cooldown, no predicate clause, no planner change, no Arena action, and no
G-1 handoff to codex_1 until the deferred set is done or the owner's ruling changes the design.
