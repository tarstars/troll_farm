---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T221237Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-25T22:12:37Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (fresh card): the P3 read is **done**; **C-12** is next, then the G-1 handoff

The predecessor card `20260825T214827Z` was discharged by the coordinator's
`20260825T215844Z` `ack_for`, so this card names nothing in `ack_for` — there is no outstanding
card of mine for it to retire.

- **Struck: the candidate-arm P3 read.** Delivered `20260825T221216Z`,
  `agent/claude_1@7ea1df9f`. **P3 is MEASURED: 0 violations over 240 seat views** — and the
  number never travels without its decomposition (guard 228 / compared-equal 12 / violation 0),
  because 228 of those zeroes are `eval_p3`'s orchard guard returning before any stream
  comparison.

## Still deferred, in the coordinator's order

1. **C-12** — per-troll idle-with-work share, with `--p4b` **ON**. Bar ≤ 1.5 %. P4b waits on
   nothing and this item is not blocked on anything.
2. Then the **G-1 handoff to codex_1** for the fresh-archive reproduction of the whole control
   set, with every carried gap listed as it stands.

## Carried gaps — unchanged, plus one the P3 read adds

- **New, from the P3 read: two published aggregates differ in sign and are both correct.** C-15's
  net cost is a delta of **own scores** (**−24**); C-16's and P3\*'s are deltas of **margin**
  (**+56**), the gap being the opponent's score falling 80. The G-1 cost table must write the
  units beside every figure or it will read as a contradiction.
- **New, from the P3 read: the candidate changes 28 of 228 non-eligible views**, exactly the
  census's 28 exchange-bearing games. That is a size, not a verdict; P1/P4/D-3 are what grade it.
- **From C-16: the scoping's price is two-sided and both sides are measured** — eligible-map dances
  untouched, **and** +39 net margin forgone across the nine firing views. Not an argument to switch
  the scoping off: the same flip produces nine P3 violations and P3 is a hard bar.
- **From C-16: the eligible class is seat-0-only in this generator** (`fuzz_panel`'s eligibility
  retry checks `specs[0]`). The P3 read's 12/12 inherits it.
- **From C-8: the exchange can silence the detector without restoring progress.** Four cases
  (`m070:1`=OSC-005, `m078:1`, `m090:1`, `m040:0`), published as failures.
- **Two windows excluded by G-D** (`m070:1` unit 0, `m084:1` unit 0): arms already diverged
  before the window opened. One looks cured, one does not; neither is claimed.
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
- The **`m061` −75 across two seats** — diagnosed (`20260825T180028Z`), awaiting that same
  ruling. The P3 read reproduces it exactly (`m061:0` −36, `m061:1` −39, both score and margin).

No Arena action taken and none proposed.
