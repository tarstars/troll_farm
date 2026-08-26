---
schema_version: 2
type: update
task_id: 20260825-dance-geometry-measurements
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T142130Z-20260825-dance-geometry-measurements-update.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260825T140431Z-20260825-dance-geometry-measurements-update.md"]
supersedes: []
created_utc: 2026-08-25T14:21:30Z
---

- To: myself (this card IS the queue item)
- CC: local_claude_1, codex_1, user
- Task: 20260825-dance-geometry-measurements
- Requires acknowledgement: yes (self-addressed; it is the card, not a receipt)

# card — replacement: the blocker moved. r1 came back REVISION_REQUIRED, r2 is published, and the gate is codex_1's again

**What changed since the previous card.** codex_1 ruled `REVISION_REQUIRED` on the r1 definitions at
`20260825T141010Z` — six minutes after my request, so the 60-minute unreviewed fallback (which would
have expired 2026-08-25T15:04:03Z) **never fired and is now dead**. Its five blockers are answered in
`claude_1/geometry1/definitions-g0-2026-08-25-r2.md` at
`agent/claude_1@192d5f1f6d52dd3815da94729abb9f196a6f9f8a` (sha256 `6a0151e0…`), delivered with the
ack-required handoff `20260825T142100Z`. **Still no M-1 or M-2 number exists** — the only things ever
run on this task are the input checks of r1 §0 (both fact-file digests match the charter, K-7 already
reproduces `8e2159e3…` byte-for-byte).

**UNBLOCK-SIGNAL — codex_1's ruling on r2, toward `claude_1`.**

1. **`DEFINITIONS_ACCEPTED`** → I build `geometry.py` and `run_geometry.py` to the accepted text and
   run G-1: whole results JSON, the controls each with its number, determinism shown, execution
   report with the headline tables.
2. **A further `REVISION_REQUIRED`** → r3, same discipline: answer every point, re-request, count
   nothing. I do not start counting on a revision I authored and nobody accepted, and a second
   revision is not a reason to lower that bar.

**No new clock.** I am deliberately **not** starting a fresh 60-minute unreviewed-fallback clock
against r2. The charter's fallback attaches to the first ack-required ruling request, codex_1 answered
it inside six minutes, and re-arming the clock on every revision would let me count on unreviewed text
by simply revising often enough. If the ruling is slow I say so in a message and ask the coordinator,
rather than proceeding quietly.

**What I do NOT do while held.** No count, no partial table, no "just the easy half" of M-1. No Arena
action, submission, TestSession, fetch or sealed-map access — this wake or any wake on this task; the
goal file authorizes none and I do not invoke the standing authorization. I write nothing outside
`claude_1/geometry1/**`, merge no peer branch, and touch neither the accepted r3 results, the
resident, the cron, nor `data/raw/games/`.

**Execution risks, carried forward unchanged from the previous card** — the v2 join's missing `chosen`
and its shim under K-9 (a K-9 failure refuses and lists the affected episodes, never drops them
quietly); the `next_cell` transliteration as the one genuinely new piece of logic, licensed by K-1 and
K-6, with the *stop and ask* rule if K-1 falls below 95 % on a residue that is not a fallback artefact;
and M-1 alone with M-2 marked **not done** — never "not needed" — if M-2 proves expensive.

**Time box 2026-08-26T14:00Z.** At the box, whatever is and is not done is written and the task stops.

DEFERRED: the G-1 build and execution, held on the signal above. Nothing else is postponed.
