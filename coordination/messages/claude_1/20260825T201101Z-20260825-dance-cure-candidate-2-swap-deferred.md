---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T201101Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T191401Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: []
created_utc: 2026-08-25T20:11:01Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (replacement): C-13 is **done and passed**; six control-set items remain, C-7 first

This card replaces `20260825T191401Z`, which it discharges by `ack_for`. Item 1 of that card is
struck: **C-13 PASSES 1 096/1 096 game-arms** (`20260825T201100Z`,
`agent/claude_1@5ad8428f`), on both the command stream and the referee transcript, run-to-run and
against an independent second build in another directory, with both poisons firing.

## Still deferred, in the coordinator's order

1. **C-7** — the poison arm P-c: the predicate gutted to "swap on every block" (no standing test,
   no beyond test, no adjacency), on which **C-5 and C-6 must both fire loudly** or they are
   inert counters. **Now the first item.** Note the shape problem to solve before running it: the
   gutted predicate can produce turns with **two or more exchanges**, which `swap_loop_control.py`
   reports as AMBIGUOUS rather than pairing by guess — so the poison's fire must be counted in a
   way that survives ambiguity, or the control will report "ambiguous" where it means "fired".
2. **C-8** — the positive-control fixture: the exchange must fire and the dance must end with
   `progress_restored`.
3. **C-16** — the R-B red half: `SWAP_P3_SCOPING_ENABLED=false` on an identical orchard-eligible
   map, where P3 must fire.
4. **The P3 read on the candidate arm.** Until it is read, **P3 is UNMEASURED, not passed**, and
   every table I publish says so. The instrument arm cannot answer it — its `MSG` diverges the
   stream at turn 1.
5. **The 11 reproduced dance fixtures with `progress_restored`.**
6. **C-12** — per-troll idle-with-work, with `--p4b` **ON**; P4b waits on nothing.

## Carried gaps, neither of them closed by C-13

- **The death direction of A-2 is unmeasured.** No own unit dies anywhere in the 274-game corpus,
  so "a unit not alive at `t-1` is absent from the read" is verified for births only. Structural
  from the full `collect()` rebuild, but an argument rather than a number. Closing it needs a
  fixture in which an own unit dies, which the fixture set does not contain.
- **C-13's own P-13b poison count is not reproducible**, by construction — a clock coin-flip,
  8/7/5 on three executions. Its gate is `> 0`. The one deliberately nondeterministic section of
  a determinism report, named here so it is not later mistaken for drift.

## Two open items that are not mine to close

- The **owner's ruling on the C-5 loop** and on the proposed Candidate 0. Nothing deferred here
  depends on it.
- The **`m061` −75 across two seats** — diagnosed (`20260825T180028Z`), awaiting that same ruling.

No Arena action taken and none proposed.
