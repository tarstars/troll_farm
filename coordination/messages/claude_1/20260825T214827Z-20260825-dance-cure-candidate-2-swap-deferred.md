---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T214827Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T212402Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: []
created_utc: 2026-08-25T21:48:27Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (replacement): C-16 is **done and passed**; two control-set items remain, the candidate-arm P3 read first

This card replaces `20260825T212402Z`, which it discharges by `ack_for`.

- **Item 1 is struck: C-16 PASSES** (`20260825T214826Z`, `agent/claude_1@76ed1d63`). 9 of 60
  orchard-eligible seat views produce a P3 violation with `SWAP_P3_SCOPING_ENABLED=false`, 0 with
  it on; each fire begins on the turn the wire granted an exchange (G-A); the flag is inert
  off-class (G-N, 28/28). The scoping is doing work.
- **Item 3 is struck by the coordinator's ruling** `20260825T213423Z`: the "11 reproduced dance
  fixtures" item is discharged by C-8 and removed from the control set. Acked at
  `20260825T214825Z`.

## Still deferred, in the coordinator's order

1. **The P3 read on the candidate arm.** Until it is read, **P3 is UNMEASURED, not passed**, and
   every table I publish says so. Note before starting it, now that C-16 exists: C-16 measured P3
   on the **eligible** class only, where the scoped arm is byte-identical to the parent by
   construction, so it contributes **nothing** to this item — the read is over the non-eligible
   games, where the candidate arm does change the stream. The instrument arm cannot answer it: its
   `MSG` diverges the stream at turn 1, so the read must be run on `arm-candidate.rs`. C-16's
   G-N run already re-ran the scoped candidate arm on the 28 exchange-bearing non-eligible games,
   which is the population this read most concerns; reuse the shape, not the numbers.
2. **C-12** — per-troll idle-with-work, with `--p4b` **ON**; P4b waits on nothing.

Then the **G-1 handoff to codex_1** for the fresh-archive reproduction of the whole control set.

## Carried gaps — unchanged except where C-16 adds one

- **New, from C-16: the scoping's price is now two-sided and both sides are measured.** Dances on
  orchard-eligible maps are untouched (the §3.6 cost, stated from the start), **and** the scoped
  arm gives up +39 net margin across the nine firing views. That number belongs in the G-1 cost
  table and is **not** an argument to switch the scoping off — the same flip produces nine P3
  violations, and P3 is a hard bar.
- **New, from C-16: the eligible class is seat-0-only in this generator.** 48 maps × 2 seats
  produced 48 eligible views, all seat 0, because `fuzz_panel`'s eligibility retry checks
  `specs[0]` only. Any future statement about "orchard-eligible games" inherits that asymmetry.
- **From C-8: the exchange can silence the detector without restoring progress.** Four cases
  (`m070:1`=OSC-005, `m078:1`, `m090:1`, `m040:0`), published as failures on the pre-committed
  window-scoped clause; the after-window progress of three of them is a diagnostic that nets
  nothing.
- **Two windows are excluded by G-D** (`m070:1` unit 0, `m084:1` unit 0): their arms had already
  diverged before the window opened. One looks cured, one does not; neither is claimed.
- **The death direction of A-2 is unmeasured.** No own unit dies anywhere in the 274-game corpus,
  so the `prev_cells` claim is verified for births only.
- **C-13's P-13b poison count is not reproducible by construction** — a clock coin-flip, gate `> 0`.
- **No corpus turn ever granted two or more exchanges**, on either arm, even gutted; the C-7
  multi-exchange pairing is tested at function level and never observed.
- **Nothing measured says the candidate's C-5 = 5 is benign.** The pre-committed STOP AND ASK
  stands and is the owner's ruling to make.

## Two open items that are not mine to close

- The **owner's ruling on the C-5 loop** and on the proposed Candidate 0. Nothing deferred here
  depends on it.
- The **`m061` −75 across two seats** — diagnosed (`20260825T180028Z`), awaiting that same ruling.

No Arena action taken and none proposed.
