---
schema_version: 2
type: progress
task_id: 20260815-oscillation-deep-dive
from: local_claude_1
to: ["user"]
cc: ["claude_1", "codex_1"]
requires_ack: false
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260821T051241Z-20260815-oscillation-deep-dive-progress.md
created_utc: 2026-08-21T05:12:41Z
artifact_ref: agent/local_claude_1
artifact_commit: 520e232d63bc7ea78df5ae2ae9a6afe021602977
artifact_paths: ["local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md"]
---

- To: user
- CC: claude_1, codex_1
- Task: 20260815-oscillation-deep-dive
- Requires acknowledgement: no

# 4b is prepared — the last sitting of the oscillation investigation, and it is short

Package: `local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md`.
4a is complete, 4c is closed; 4b stamps whatever is left, and then the whole
investigation closes.

## What the preparation found

All 34 recorded cases were re-graded **against the champion you kept this
morning** rather than against the old resident the library was frozen on, and
they fall into six buckets:

- **8 are simply FIXED** on the current champion — nothing to stamp.
- **6 are clean stamp candidates**, each with a proposed one-line reason: the
  four NOT-STARVED cases (three of which the troll never waited a single turn
  in), the single-troll game where no pairing decision exists, and OSC-012,
  where the troll waited 193 turns and the instrument measured **zero** turns
  with usable work — the one case where waiting was provably right.
- **18 are the benching class you already ruled a BUG** on 2026-08-20. They need
  no new ruling; they close as *known-open* with the cure sitting on the shelf.
- **2 — OSC-032 and OSC-033 — are the only real decision in the sitting.**

## The one real decision

OSC-032 and OSC-033 are stall-kind cases that were never assigned to a class.
The troll waited 110 and 143 turns respectively, and in **every one of those
turns work was available to it**. Read literally that is rule R-2, your own
rule, calling them bugs — but they are not benching cases, so the P1+P2 cure on
the shelf does not touch them and nothing else is chartered that would. Three
options are laid out in the package (fold into R-2 as known-open / stamp them
accepted / charter a small look at why no goal was ever assigned). My
recommendation is the first.

## Two facts I did not expect, both measured

1. **The champion you kept beats the bot it replaced on the frozen cases: 8
   FIXED versus 3, and not one case lost.** OSC-003, OSC-006, OSC-014, OSC-020
   and OSC-034 are fixed by Door 1 and were not fixed by cure C. The Arena
   called the same step immaterial. Both readings are honest — the Arena is
   measuring score against live opponents, the grader is measuring whether these
   specific frozen situations still reproduce — and it is worth knowing that
   this morning's KEEP is better supported than the Arena number alone suggests.
2. **OSC-031 — the case that started the 4c thread — is still NOT FIXED on the
   champion.** The chop defect you ruled was real and was fixed; what is still
   firing in that game is the benching, which is the other disease. Said out
   loud here so it is not rediscovered later as a surprise.

Nothing in this package changes any code, and no Arena action is taken or
authorized. Session 3 continues untouched.
