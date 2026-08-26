---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T191401Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T185203Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: []
created_utc: 2026-08-25T19:14:01Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (replacement): C-11 is **done and passed**; seven control-set items remain, C-13 first

This card replaces `20260825T185203Z`, which it discharges by `ack_for`. Item 1 of that card is
struck: **C-11 PASSES 54 800/54 800 turns, 100.00 %** (`20260825T191400Z`,
`agent/claude_1@090ced1a`), by the print-only arm the card named as the cheaper route. The stale
`m061` line the coordinator flagged in the previous card is **not carried forward** — `m061` is
diagnosed; what is open there is the owner's ruling on Candidate 0.

## Still deferred, in the coordinator's order

1. **C-13** — determinism: two runs with explicit `--label`/`--peer-label`, byte-identical
   outputs. **Now the first item.** Cheapest remaining control and it gates the credibility of
   every number already published, including C-10's and C-11's.
2. **C-7** — the poison arm P-c: the predicate gutted to "swap on every block", on which C-5 and
   C-6 must both fire loudly or they are inert counters. Note that C-11 now has its **own** poison
   control (`c11_poison_control.py`, 913/6 800, 34 of 34 fixtures) — the C-7 item is unchanged and
   is about C-5/C-6, not about C-11.
3. **C-8** — the positive-control fixture: the exchange must fire and the dance must end with
   `progress_restored`.
4. **C-16** — the R-B red half: `SWAP_P3_SCOPING_ENABLED=false` on an identical orchard-eligible
   map, where P3 must fire.
5. **The P3 read on the candidate arm.** Until it is read, **P3 is UNMEASURED, not passed**, and
   every table I publish says so. The instrument arm cannot answer it — its `MSG` diverges the
   stream at turn 1.
6. **The 11 reproduced dance fixtures with `progress_restored`.**
7. **C-12** — per-troll idle-with-work, with `--p4b` **ON**; P4b waits on nothing.

## One new item this wake put on the list

- **The death direction of A-2 is unmeasured.** No own unit dies anywhere in the 274-game corpus,
  so "a unit not alive at `t-1` is absent from the read" is verified for births only. Closing it
  needs a fixture in which an own unit dies, which the fixture set does not currently contain. It
  is **not** a blocker on C-11's PASS — the write is a full `collect()` rebuild, so a stale entry
  is structurally impossible — but it is a named gap, not a covered one, and it should not
  disappear because the headline number is 100 %.

## Two open items that are not mine to close

- The **owner's ruling on the C-5 loop** and on the proposed Candidate 0. C-10 and C-11 both
  passing narrow the possibilities: the reversals are real cell exchanges (C-10) driven by a
  correct memory (C-11), so if the loop is a defect it is in the predicate's *selection*, not in
  its inputs. Nothing I have deferred depends on the ruling.
- The **`m061` −75 across two seats** — diagnosed, awaiting the owner's ruling on Candidate 0.

No Arena action taken and none proposed.
