---
schema_version: 2
type: policy
task_id: 20260826-candidate-3-keep-your-goal
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T113907Z-20260826-candidate-3-keep-your-goal-policy.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-26T11:39:07Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260826-candidate-3-keep-your-goal
- Requires acknowledgement: yes — an owner ruling that bounds this task

# policy: OWNER RULING ~11:30Z — Candidate 3 is **bounded**: one r5, one review, one panel, one reproduction, one owner read, then STOP; no Candidate 2 re-run unless the panel shows an own-score gain; the champion is back on the ladder (`41197542`)

Transcribed from the coordinator session of 2026-08-26 ~11:30Z, after the coordinator's critical
review of the project (the dance/stall phenomenon has a corpus ceiling of ≈1.4 points; the dance-only
cost is not established; the ladder saw the previous two cure generations as ≈0.00; Candidate 3 is a
fix for Candidate 2's loop, i.e. a cure for a cure). The owner ruled three things; two bind here.

## (a) The bound — binding on this task

Candidate 3 gets **exactly**: G-0 **r5** (claude_1) → **one** codex_1 review → if accepted, **one**
build + panel (G-1) → **one** codex_1 reproduction → the diff on `main` → **one** owner read. Then
the task **stops, whatever the outcome**. A second BLOCK at r5, or a G-1 that fails its own
pre-commitments, closes the task — no r6, no re-tuning. **Candidate 2 is re-run on top only if
Candidate 3's panel shows an own-score gain** (points, not margin, not "C-5 = 0"). Rulings
`110544Z`/`110904Z` (C + capacity middle; P4b evaluable via `20260826-p4b-narrator-param`) stand
inside the bound. The P4b charter is not bounded by this message; it is an instrument repair.

## (b) The ladder measures again — information, not work

The champion `547fa706…` was resubmitted at 11:38:25Z, submission **`41197542`**, hash verified,
one mutation call. The NARRATE instrument leaves the ladder. **Nobody else touches the Arena.** No
Candidate 3 platform measurement is authorized.

## (c) The goals, as the owner stated them

**≥ 25.40 stands and is not the only goal: control over the code and its cleanliness are goals
too.** The current line — readable source, diffs in files, the owner reading every change — is the
code clean-up line, and it is wanted for its own sake, not only for points. **The next item after
it is the banana farm**; the coordinator's assessment goes to the owner first, no charter yet.

## Order

Unchanged: claude_1 writes r5; codex_1 starts the P4b charter and reviews r5. Both: read this as the
charter's ceiling and plan the packet to be the last one.
