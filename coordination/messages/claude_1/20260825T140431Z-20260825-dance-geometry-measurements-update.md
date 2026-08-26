---
schema_version: 2
type: update
task_id: 20260825-dance-geometry-measurements
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260825T140431Z-20260825-dance-geometry-measurements-update.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-25T14:04:31Z
---

- To: myself (this card IS the queue item)
- CC: local_claude_1, codex_1, user
- Task: 20260825-dance-geometry-measurements
- Requires acknowledgement: yes (self-addressed; it is the card, not a receipt)

# card — G-0 is delivered and the gate is codex_1's; I hold the build and start no count until the gate opens

State at this stamp: claimed inside the 30-minute window; G-0 published at
`agent/claude_1@1bd2c257c1181546c1270d98042400fa37e0e700`,
`claude_1/geometry1/definitions-g0-2026-08-25.md` (sha256 `4cf447f5…`); the ack-required ruling
request went to codex_1 at `20260825T140403Z`. **No M-1 or M-2 number exists.** Input checks only:
the two fact files hash to the charter's digests, and K-7 already reproduces `8e2159e3…`
byte-for-byte.

**UNBLOCK-SIGNAL — either of these, whichever lands first:**

1. **codex_1 publishes the G-0 ruling toward `claude_1`.** On `DEFINITIONS_ACCEPTED` I build
   `geometry.py` and `run_geometry.py` to the accepted text and run G-1. On
   `REVISION_REQUIRED` I publish `definitions-g0-2026-08-25-r2.md` answering every point, and
   I re-request the ruling; I do **not** start counting on a revision I authored and nobody accepted.
2. **The 60-minute clock expires** — 2026-08-25T15:04:03Z, sixty minutes after the ruling request.
   Then, and only then, I proceed with the published definitions marked **unreviewed**, and the G-1
   handoff says so in terms, so codex_1 reviews definitions and execution together. The card's
   fallback is a permission to proceed, not a finding that the definitions are sound.

**What I do NOT do while held.** No count, no partial table, no "just the easy half" of M-1. No
cure, no Candidate 2 or 3, no bug ruling, no bot change. No Arena action of any kind — no
submission, no TestSession, no fetch, no sealed-map access — this wake or any wake on this task;
the goal file authorizes none and I do not invoke the standing authorization. I do not write
outside `claude_1/geometry1/**`, I do not merge any peer's branch, and I do not touch the
accepted r3 results, the resident, the cron, or `data/raw/games/`.

**Known execution risks, recorded now so they are not discovered as excuses later.**

- The v2 join (batches 1 and 2, 309 of the older read's 469 games) emits no `chosen`; the shim and
  its control K-9 are the answer, and if K-9 fails on a batch the affected episodes are **refused
  and listed**, never quietly dropped.
- The `next_cell` transliteration is the only genuinely new logic; K-1 and K-6 license it. If K-1
  falls below the 95 % bar and the residue is not a fallback artefact, the card's *Stop and ask*
  rule fires — the coordinator and the owner are told, and I do not publish the tables as if the
  measurement were the arm's geometry.
- If M-2 proves expensive I deliver M-1 alone and mark M-2 **not done**, never "not needed".

**Time box 2026-08-26T14:00Z.** At the box, whatever is and is not done is written and the task
stops. Progress lease 15 minutes without concrete evidence; G-0 is this wake's evidence.

DEFERRED: the G-1 build and execution, held on the two signals above. Nothing else is postponed.
