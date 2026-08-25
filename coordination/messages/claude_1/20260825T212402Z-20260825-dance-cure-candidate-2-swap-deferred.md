---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T212402Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T205731Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: []
created_utc: 2026-08-25T21:24:02Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (replacement): C-8 is **done and passed**; four control-set items remain, C-16 first

This card replaces `20260825T205731Z`, which it discharges by `ack_for`. Item 1 of that card is
struck: **C-8 PASSES** (`20260825T212251Z`, `agent/claude_1@a84e764a`) — the exchange ends **9**
distinct dances with progress restored, three of them exactly a frozen library episode, over 240
games; N-1 inert control 0 passes on all 27 cases; G-B/G-D/G-R gates pass; re-run byte-identical.
**With a named cost that is now part of the record: 4 of the 13 firing cases are
detector-quiet-but-stalled.**

## Still deferred, in the coordinator's order

1. **C-16** — the R-B red half: `SWAP_P3_SCOPING_ENABLED=false` on an identical orchard-eligible
   map, where P3 must fire. **Now the first item.** Note before starting it: C-16 and item 2 are
   the same subject from two sides — C-16 asks whether the scoping *can* fire, item 2 asks whether
   it *does* on the candidate. Doing C-16 first gives item 2 a live instrument to be read with.
2. **The P3 read on the candidate arm.** Until it is read, **P3 is UNMEASURED, not passed**, and
   every table I publish says so. The instrument arm cannot answer it — its `MSG` diverges the
   stream at turn 1.
3. **The 11 reproduced dance fixtures with `progress_restored`.** C-8 changes what this item can
   mean and the change should be ruled before it is run: the 11 are the fixtures the **champion**
   reproduces, and the candidate reproduces **none** of the twelve exchange-bearing ones
   (12/12 `NOT_REPRODUCIBLE_ON_BASE`, measured this wake). So this item is either (a) a champion
   measurement, which is what it literally says and which C-8 does not supply, or (b) a restatement
   of C-8 on the candidate, which is now delivered. I will not silently pick one.
4. **C-12** — per-troll idle-with-work, with `--p4b` **ON**; P4b waits on nothing.

## Carried gaps

- **New, from C-8: the exchange can silence the detector without restoring progress.** Four cases
  (`m070:1`=OSC-005, `m078:1`, `m090:1`, `m040:0`). Three of the four units progress after the
  window closes and the fourth's window ends at the game's last turn — a reported diagnostic, not
  a verdict, and the four remain failures on the pre-committed window-scoped clause. `m090:1`
  granted **three** exchanges inside one eight-turn window with no progress from any of them,
  which is what a C-5 repeat looks like from the progress side and is worth naming beside the C-5
  stop.
- **Two windows are excluded by G-D** (`m070:1` unit 0, `m084:1` unit 0) because they open after
  their arms had already diverged. One looks cured and one does not; neither is claimed.
- **The death direction of A-2 is unmeasured.** No own unit dies anywhere in the 274-game corpus,
  so the `prev_cells` claim is verified for births only. Closing it needs a fixture in which an own
  unit dies, which the fixture set does not contain.
- **C-13's P-13b poison count is not reproducible by construction** — a clock coin-flip, gate `> 0`.
- **No corpus turn ever granted two or more exchanges**, on either arm, even gutted; the C-7
  multi-exchange pairing is tested at function level and never observed.
- **C-8 says nothing about whether the candidate's C-5 = 5 is benign.** The pre-committed STOP AND
  ASK stands and is the owner's ruling to make.

## Two open items that are not mine to close

- The **owner's ruling on the C-5 loop** and on the proposed Candidate 0. Nothing deferred here
  depends on it.
- The **`m061` −75 across two seats** — diagnosed (`20260825T180028Z`), awaiting that same ruling.
  Note in passing that `m061:0` is one of C-8's nine passing cases, and it is also one of the two
  seats of that −75 (−36 at seat 0, −39 at seat 1, the corpus's two worst single-game deltas). The
  same game carries both a cured dance and a large score loss. Neither fact answers the other.

No Arena action taken and none proposed.
