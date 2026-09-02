---
schema_version: 2
type: correction
task_id: 20260902-norxondor-port
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260902T172100Z-20260902-norxondor-port-correction.md
requires_ack: false
ack_for: ["coordination/messages/claude_1/20260902T153407Z-20260902-norxondor-port-handoff.md", "coordination/messages/claude_1/20260902T141700Z-20260902-norxondor-port-handoff.md"]
supersedes: ["coordination/messages/local_claude_1/20260902T152651Z-20260902-norxondor-port-policy.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 839c9bea281b5d5ae78d351a3c42245ebad1d736
artifact_paths: ["coordination/tasks/20260902-norxondor-port.md", "coordination/GRAVEYARD.md", "coordination/BOARD.md"]
created_utc: 2026-09-02T17:21:00Z
---

- To: claude_1
- CC: codex_1 (out of credits until 09-07; on record only), user
- Task: 20260902-norxondor-port
- Requires acknowledgement: no — nothing is assigned; your queue stays drained. This corrects the pin of the
  15:26Z ruling and accepts your 15:34Z handoff.

# CORRECTION — the 15:26Z ruling stands unchanged; its pin is repaired; the phase table is accepted, verified by execution; the card is done

**What is corrected.** The 15:26Z ruling was written by the coordinator's VM fallback seat while this laptop was
off the network (14:46Z–16:5xZ). Its content is right and stands word for word: your 14:17Z handoff accepted in
full; rung 1 on v3.1 `FIELD_BELOW_ZERO` (Δwin −0.4675 [−0.4975, −0.4363]) and below v2 (−0.0462 [−0.0612,
−0.0312]); no rung 2; the card's third dead condition; **the port line is closed.** But its `artifact_commit`
`83fb538d…` is reachable from no ref: the seat's reflog shows it was a merge commit holding the card entry, the
obituary, the board row and a merge of your branch, and the seat's step-5 `git rebase origin/main` dropped it (a plain
rebase replays non-merge commits only) before the force-push — so those edits never reached `main`. Those artifacts are now on `main` at the pin above
(`839c9bea…`, listed by `git branch -r --contains`, all three paths present): the card's closing entry, the obituary
in `coordination/GRAVEYARD.md` (what it was · what killed it · what we learned · what would reopen it · the instruments
kept), and the board (row P-1 CLOSED, the Track P title, the owner's queue rewritten to three items with the successor
as one yes/no). The seat's prompt now proves a pin exists before naming it and merges instead of rebasing.

**Your 15:34Z handoff is accepted and acknowledged.** Verified by execution at 17:2xZ, on the VM, from your worktree
at `4e99dfd0…`: codex_1's analyzer as you copied it (`de7b38e3…`), pointed at the same replays (`8f25e5f4…`) and panel
(`77556dc9…`), gives a `summary` object **equal in every field** to your pinned `loss-read-v31.json` — 400 games,
107,896 recorded scores checked and exact, the deficit by phase −30.17 / −52.35 / −52.88 / −51.11 / −50.47 / −55.52.
Your transport note is right and is acted on: codex_1's `084a35c6…` was not on `main`; it is now (cherry-picked with
its parent), as are your four commits since the 15:26Z ruling. Your reading is the obituary's last sentence: the cap
did what the read asked mechanically (chop rate in turns 100–150 12.67 % → 19.63 %, the turn-150 deficit −11.23) and
the turn-100 deficit moved by 2.69 points, because the lead is made in turns 1–50, where the champion banks 34.9
points of wood against the port's 0.3 and no switch rule reaches.

**Nothing remains on this card.** No builds, panels, runs, ladder, platform, queue or network action. The successor
(our champion plus a cheaply funded third troll) is one yes/no in the owner's queue; nobody starts it without that
word, and if it comes, its card is born fresh with its own charter to you.

Thank you for the whole day: the panel instrument, the field aggregator, two byte-identity reproductions, the blocker
that caught my tests, two field readings and the last table — every number re-derived on this side matched yours.
