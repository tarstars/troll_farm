# H-STARVE-1 increment-1 instrument review — 2026-08-16

Verdict: **THE TWO NARROW ROWS ARE ACCEPTED; INSTRUMENT REVISION_REQUIRED BEFORE THE
FULL SPECIMEN TABLE.**

Reviewed artifact `4fc5439dbe496b2066767d45006c487e77c5e037` independently:

- audit output reproduces OSC-001 MAIN 195/195 and OSC-012 MAIN 193/193;
- both show zero committed turns, zero empty lists, and all targets `None` throughout;
- command streams are byte-identical on **both** specimens when independently checked
  (the committed runner checks only the first);
- the resident remains byte-exact `98628e98…`;
- in this source, WAIT is the sole `Target::None` constructor, so `all_none=true` is a
  valid static proxy for “every candidate is WAIT” for these two rows.

Thus the narrow statement is supported: on these two windows the explicit blocker is
routed through MAIN, holds no regeneration commitment, and receives nonempty all-WAIT
candidate lists. `ALL_WAIT_CAUSE_UNDETERMINED` is the correct label; the data cannot yet
separate no world work from a generator gap.

## Blocking instrument defects before expansion

1. **Parked-unit selection is wrong outside these two-unit D1 cases.** `classify()`
   treats every own unit other than `window.unit` as parked. D1 situations already carry
   the explicit `classification.blocker.unit`, which must be used. For `P4_STALL`, the
   window unit is itself the stalled anchor, so the current exclusion audits the other
   unit—the opposite of the charter. With three own units it would also emit multiple
   unproven “parked” rows.
2. **Parsing/coverage can fail silently.** There is no assertion of exactly one row for
   the selected unit on every integer turn in `[turn_start, turn_end]`, no duplicate-turn
   rejection, and no failure on missing/malformed diagnostic lines. An inert or partial
   logger can therefore produce a shorter or empty table without voiding the run.
3. **The chartered candidate summary is incomplete.** The logger records count and the
   boolean `all_none`, but not candidate kinds/commands or the chosen candidate. The
   current WAIT equivalence is verified only by a source-wide uniqueness fact and will
   silently drift if another `Target::None` candidate is added. Log a compact direct
   histogram plus the post-selection chosen command/target, tied to the same unit/turn.
4. **Non-interference must be per specimen.** The committed runner compares commands on
   only the first situation. The full table must void on divergence in any situation.
5. **Avoid stderr pipe backpressure.** stderr is drained only after the turn loop. A
   multi-unit 200-turn diagnostic stream can fill the pipe and deadlock. Drain
   concurrently or write stderr to a temporary file.

Increment 2 should add `work_remaining` only after these instrument-validity repairs.
For each label, add a negative control that changes only its decisive signal; keep the
Packet-lite SLICE and no-cure boundaries.
