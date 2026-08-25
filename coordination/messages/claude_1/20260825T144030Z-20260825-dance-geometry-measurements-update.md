---
schema_version: 2
type: update
task_id: 20260825-dance-geometry-measurements
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T144030Z-20260825-dance-geometry-measurements-update.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T142130Z-20260825-dance-geometry-measurements-update.md"]
supersedes: []
created_utc: 2026-08-25T14:40:30Z
---

- To: myself (this card IS the queue item)
- CC: local_claude_1, codex_1, user
- Task: 20260825-dance-geometry-measurements
- Requires acknowledgement: yes (self-addressed; it is the card, not a receipt)

# card — replacement: the pin moved twice, R1–R5 are accepted on their text, and the only thing left open is codex_1's ruling on `858b5c37`

**What changed since the 14:21:30Z card.** That card pinned r2 at `192d5f1f`. Two reviews landed
after it and the artifact moved twice:

- `local_claude_1/20260825T141645Z` (policy) supplied the hold-counter construction fact. I verified
  it in the arm (`:734`, `:742`, `:907`, `:962–970`) and adopted it, narrowed by **N-1** (the counter
  is game-scoped, so the window's first turn is uncovered) and **N-2** (`:938` disables the hold
  game-wide under P3 scoping) → §R4a at `2dc0d03c`, correction `20260825T142800Z`.
- `codex_1/20260825T142040Z` reached N-2 independently and named the three scope-disabled
  episode-bearing games; census re-derived from the pinned file — **3 of the 25 episodes** →
  `858b5c37`, handoff `20260825T143500Z`.
- `codex_1/20260825T142337Z` ruled **R1–R5 accepted on the text** and `REVISION_REQUIRED` **solely
  for canonical redelivery**, since the delivered pin predated §R4a. Redelivered at
  `20260825T144000Z` on `858b5c37` (sha256 `36af779a…`), lint clean.

**Still no M-1 or M-2 number exists.** The only things ever run on this task are the input checks and
K-7 (already reproducing `8e2159e3…` byte-for-byte), plus the two census re-derivations above, which
are checks on inputs and not measurements.

**UNBLOCK-SIGNAL — codex_1's ruling on `858b5c37`, toward `claude_1`.**

1. **`DEFINITIONS_ACCEPTED`** → build `geometry.py` and `run_geometry.py` to the accepted text and run
   G-1: whole results JSON, every control with its number, determinism shown, execution report with
   the headline tables. codex_1 has said he expects acceptance without a further conceptual revision
   unless the bytes differ from the text he reviewed — I make no assumption on that and start nothing
   until the ruling is published.
2. **A further `REVISION_REQUIRED`** → r3, same discipline: answer every point, re-request, count
   nothing.

**No new clock**, for the same reason as the previous card: the charter's 60-minute unreviewed
fallback attached to the first ruling request, was answered in six minutes, and re-arming it on each
revision would let me count on unreviewed text by revising often enough.

**What I do NOT do while held.** No count, no partial table, no "easy half" of M-1. No Arena action,
submission, TestSession, fetch or sealed-map access. Nothing written outside `claude_1/geometry1/**`;
no peer branch merged; the accepted r3 results, the resident, the cron and `data/raw/games/`
untouched.

**Execution risks, carried forward unchanged**: the v2 join's missing `chosen` and its shim under K-9
(failure refuses and lists the affected episodes, never drops them); the `next_cell` transliteration
as the one genuinely new piece of logic, licensed by K-1/K-6, with *stop and ask* if K-1 falls below
95 % on a residue that is not a fallback artefact — now reported as two residue lines, scope-active
and scope-disabled; M-1 alone with M-2 marked **not done**, never "not needed", if M-2 proves
expensive.

**Time box 2026-08-26T14:00Z.**

DEFERRED: the G-1 build and execution, held on the signal above. Nothing else is postponed.
