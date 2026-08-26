# WORKING RULES — how work is organised on this project (owner-adopted 2026-08-26)

Read this before anything else in `coordination/`. It is short on purpose. The transport
protocol (`multi-agent-protocol.md`) says *how messages are formed*; this file says *how work
moves*. Where the two seem to disagree, this file wins on organisation and the protocol wins on
message format.

**Why this file exists.** The project is a graveyard of started-then-stalled initiatives. The
causes, measured on 2026-08-26: design reviews with no round limit (r1…r6, zero code); tasks born
without a written "done"; broken measuring instruments that nobody owned; the ladder idle for
days while 1,800+ messages were exchanged; results left on side branches; every decision routed
through one coordinator. Each rule below closes one of those.

## 1. The board is the record

- `coordination/BOARD.md` is **the one file the owner reads**. One row per task in motion, grouped
  by track. **At most two rows per track** (one active, one queued). *Not on the board = not
  happening.*
- Whoever moves a task updates its row **in the same commit**: stage, *next concrete step*,
  blocked-on, last day with evidence. A row nobody updates is a row the owner cannot see.
- Tracks now: **D** dancing trolls (finish, submit, verdict, close), **T** top-10 analytics,
  **F** banana farm, **0** instruments (the measuring tools themselves).

## 2. Every task is born with three sentences

In its card under `coordination/tasks/`:

- **Done means** — the artifact, where it lands, what it must contain.
- **Dead means** — the condition under which we stop and write the obituary.
- **Budget** — review rounds, calendar days, ladder slots, builds.

A card without these three is not chartered.

## 3. Stages are the same for every track

**Read → Design (≤ 2 review rounds) → Build (validity gates first) → Panel (one) → Ladder (one
block) → Verdict written.**

- **Two review rounds, then decide or kill.** A second BLOCK on the same packet ends the design;
  the coordinator either rules the open point or kills the task. There is no r3. A one-line
  mechanical defect may be returned as ACCEPT-WITH-EDIT, naming the exact edit.
- **Validity before value.** No value number (score, margin) is read until the bot runs cleanly
  on the panel (no new blocked games, no no-progress turns, byte-identity where the rule is off).
- **The panel is a ticket, not a verdict.** A panel pass buys exactly one ladder slot. The
  ladder is the judge (the local panel has been wrong by ten points on a real bot).

## 4. Stalls are visible, deaths are written

- A row with **no evidence for two days**, or **over its budget**, is marked **STALLED** by
  whoever notices (the coordinator at every session). It goes to the owner as one line:
  *kill or extend?*
- A killed task gets **one paragraph in `coordination/GRAVEYARD.md`** the same day: what it was ·
  what killed it · what we learned · what would reopen it. Closed, not "in progress".

## 5. Mail is for handoffs and verdicts

- Send a message when you **hand off an artifact**, **return a verdict**, **charter**, or
  **ack** what requires an ack. Nothing else. Design discussion lives in the task's files.
- Every ruling toward another agent is `requires_ack: true`; a bare receipt wakes nobody.
- After publishing, re-run the sweep and confirm the message is live. A handoff's pinned commit
  must already be on the remote (push the artifact commit first; the pre-push lint reads the
  worktree, so park unpublished messages outside it while pushing).
- Stamps come from `date -u` in the command that writes the file.

## 6. The ladder is one queue

- The queue is at the bottom of the board. **One bot on the ladder at a time**; one slot = an
  8-read self-replacement block ≈ 16 h. A slot may be booked only with a panel pass in hand.
- Only the Arena controller (`local_claude_1`) submits; nobody else touches the Arena.
- No verdict on fewer than the slot's reads (σ ≈ 1.5 per read).

## 7. Everything lands on `main` at every gate

The diff (`readable/diffs/<candidate>.diff` on the readable source), the panel report, the
verdict — integrated by the coordinator at the gate, not at the end. Results that live on a side
branch are results the project forgets.

## 8. Roles and the daily routine

- **A bot** (claude_1, codex_1): at most one *build* task and one *read/review* task at a time.
  Wakes on ack-required mail → works its card → updates its row → one handoff at the gate.
- **The coordinator** (`local_claude_1`): once a day or when the owner says — reads all mail
  whole *before* publishing anything; rules on charters, kills, ladder bookings and the
  two-rounds-are-up decisions; walks the board and marks stalls; runs the ladder queue; keeps
  `main` == its branch. Does **not** write designs, read code for the bots, or referee review
  loops.
- **The owner**: one conversation a day (§9). Judges from the game state down, never from the
  code up. Decisions are one word where possible and are logged, dated, in the board's
  Decisions list so nobody asks twice.

## 9. The owner conversation — the routine

The owner says **"board"**. The coordinator answers in this fixed shape, every time:

1. **Moved** — rows with evidence since last time, one line each, with the number that matters.
2. **Stalled / over budget** — each ending in *kill or extend?*
3. **Ladder** — what is on it, the newest read, what is next and when.
4. **Decisions for the owner** — at most three, each answerable in one word.
5. **Corrections** — anything the coordinator got wrong since last time, said out loud.

Then a conversation. Answers come from evidence in the repo, not from memory; "I don't know,
I'll find out by next session" is a valid answer.

**Worth the owner's time** (only the owner can decide): kill or extend; priority between tracks
when they compete for a bot or the ladder; go/no-go at the cheap gates (after a read, after a
panel); verdicts on code the owner reads (the code-control goal); scope changes.
**Not worth the owner's time** (the coordinator decides and reports): who does which task;
review-round outcomes; message traffic; instrument repairs; integration; charter wording.
If the coordinator brings one of these anyway, the owner says "decide it yourself".

## 10. Plain words

All owner-facing text — board rows, verdicts, questions — in plain words, every code or
abbreviation explained at first use. If a row needs jargon to understand, the row is the defect.

## 11. Goals, as the owner stated them (2026-08-26)

A mature ladder score **≥ 25.40** stands, **and it is not the only goal: control over the code
and its cleanliness are goals too.** A change the owner cannot read is not finished. The current
line is the code clean-up (readable source, diffs in files); the next item is the banana farm,
gated on Track T's and F's reads.
