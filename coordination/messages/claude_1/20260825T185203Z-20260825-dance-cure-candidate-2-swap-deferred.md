---
schema_version: 2
type: blocker
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T185203Z-20260825-dance-cure-candidate-2-swap-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T183357Z-20260825-dance-cure-candidate-2-swap-deferred.md"]
supersedes: []
created_utc: 2026-08-25T18:52:03Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DEFERRED (replacement): C-10 is **done and passed**; eight control-set items remain, C-11 first

This card replaces `20260825T183357Z`, which it discharges by `ack_for`. Item 1 of that card is
struck: **C-10 PASSES 66/66** (`20260825T185202Z`, `agent/claude_1@b6f9413e`). Item 10 is struck
too: the transport switchover landed and my `scripts/` are refreshed from `main@6a8d4db0`, with
the drift-free sweep quoted in `20260825T185200Z`. Everything else is untouched and I am not
pretending otherwise.

## Still deferred, in the coordinator's order

1. **C-11** — the `prev_cells` check (A-2). **Now the first item.** Note the shape problem before
   starting: the v5 wire does **not** carry each unit's `prev_cells` read, so C-11 cannot be done
   the way C-10 was — it needs either a print-only diagnostic arm (the `arm-diagnostic.rs` pattern,
   which cost one `eprintln!` triple and a G-A print-only gate) or a wire extension, and the
   print-only arm is the cheaper and less invasive of the two. That choice is the first decision of
   the next wake, not a thing to discover mid-run.
2. **C-13** — determinism (same spec, same stream, twice).
3. **C-7** — the poison arm: C-5 and C-6 must fire loudly on it, or they are inert counters.
4. **C-8** — the positive-control fixture.
5. **C-16** — the R-B red half.
6. **The P3 read on the candidate arm.** Until it is read, **P3 is UNMEASURED, not passed**, and
   every table I publish says so. The instrument arm cannot answer it — its `MSG` diverges the
   stream at turn 1.
7. **The 11 reproduced dance fixtures with `progress_restored`.**
8. **C-12** — per-troll idle-with-work, with `--p4b` **ON**; P4b waits on nothing.

## Two open items that are not mine to close

- The **owner's ruling on the C-5 loop** and on the proposed Candidate 0. C-10 passing makes the
  loop more certain, not less — the reversals are real cell exchanges — so the ruling matters more
  today than it did yesterday. Nothing I have deferred depends on it.
- The **`m061` −75 across two seats**, still undiagnosed and still, in my judgement, the more
  dangerous of the two findings for G-3's −1.0 floor.

No Arena action taken and none proposed.
