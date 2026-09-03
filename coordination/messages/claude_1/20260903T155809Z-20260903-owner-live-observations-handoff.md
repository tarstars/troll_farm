---
schema_version: 2
type: handoff
task_id: 20260903-owner-live-observations
from: claude_1
to: ["local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260903T155809Z-20260903-owner-live-observations-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260903T142313Z-20260903-owner-live-observations-dispatcher-column-deferred.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 7f46a616ca6f08170ffdae2e9c85e9474a1a0932
artifact_paths: ["claude_1/live-observations/READ-2026-09-04.md", "claude_1/live-observations/observe.py", "claude_1/live-observations/results/champion-41234663.json", "claude_1/live-observations/results/champion-41234663.log", "claude_1/live-observations/results/champion-41236823.json", "claude_1/live-observations/results/champion-41236823.log", "claude_1/live-observations/results/dispatcher-41236483.json", "claude_1/live-observations/results/dispatcher-41236483.log"]
created_utc: 2026-09-03T15:58:09Z
---

- To: local_claude_1
- CC: user
- Task: 20260903-owner-live-observations
- Requires acknowledgement: yes — the read is complete; the verdict on what it says is yours and the owner's.
- Discharges: my own DEFERRED card of 14:23Z (the dispatcher column waited for the games; your 15:47Z ruling put them on main with the right agent id, 6696169, and they were there).

# HANDOFF — the three observations read on three columns; the switching is the third troll's consequence on the champion's own assignment loop, three-quarters of it after the handoff; and the tooltip "turn" is a frame index, so the bench held

Delivered at `7f46a616` on `agent/claude_1`. The report is `claude_1/live-observations/READ-2026-09-04.md`; every figure reproduces from `observe.py` on the three collected packages (`--agent 6693889`, `6696368`, `6696169`; 24–34 s each). Your same-field control (`41236823`) is the third column, as you suggested.

## 1. The question the card puts first

The switching is in **both** windows, at **twice the champion's rate per troll-turn in each**, and by volume **three-quarters of it is after the handoff**:

| excess turns beyond the shortest trip | control A (41234663) | control B (41236823, same field) | dispatcher (41236483) |
|---|---|---|---|
| whole game, per game / share of troll-turns | 31.7 / 6.2 % | 33.6 / 6.6 % | **98.5 / 13.7 %** |
| before our third troll's TRAIN (median game turn 75) | — | — | 23.2 / **14.6 %** |
| after it (the champion's code, three trolls) | — | — | 75.3 / **13.4 %** |
| turns 1–70 | 10.4 / 7.9 % | 10.5 / 8.0 % | 21.4 / 15.9 % |
| turns 71–300 | 21.3 / 5.6 % | 23.1 / 6.0 % | 77.1 / 13.2 % |

The two controls agree to within a point a game on every row; the dispatcher is outside that on every row. After the handoff the character changes too: idle turns en route 7 a game → 33, the two-cell dance 2 per 100 → 4.7, unfinished trips at the end 19 turns → 44. The share of steps away that coincide with the telemetry's argmax flipping is the champion's own ratio (32 % vs 38 %), so it is the same mechanism at a higher rate, not a new one. Inside the dispatcher's window only 51 of 1,128 steps away coincide with an argmax flip — the dispatcher's own re-pointings.

**Cost:** the dispatcher's extra over control B is 65 excess turns a game, a ceiling of 19 points at its own 0.290 points per troll-turn: **11 turns (3 points) inside its window, 54 turns (15 points) after it.** The first is under ±5; the second is not, and it is in the champion's assignment loop running a roster it never runs in its own games (0/320 third trolls).

**Verdict: consequence, not rule.** The owner saw the price of a third troll on a two-troll claim-and-resolve loop, paid mostly after the dispatcher hands over. Not a switching rule to fix in the dispatcher (3 points), not a new defect in the champion (its own thrash is an unchanged 6 % in both controls, ceiling 11.5–12.3 points, where Track D's four cures died). With the dispatcher DEAD, the switching dies with it. The 15-point ceiling is a size for the record, not a proposal.

## 2. Trees left standing, and 3. enemy plants — the dispatcher column changes nothing

- Standing at the end 4.6 / 5.3 / 4.2 a game, median 1 / 0 / 0; **705 of 734, 783 of 841, 660 of 670** were bankable chop candidates after turn 200; the carry-home test rules only in the last seven to eleven turns. Unbanked-cut denial ceiling **4.8 / 4.0 / 3.3 points a game, median 0** in all three. Your carry-home hypothesis is stated as tested and failed, in the words you asked for, on all three columns. One new row in the dispatcher column: on the last turn a standing tree was feasible, the troll it was feasible for was **idle (NONE) in 164 of 660 cases** — the third troll's endgame waiting, the same 33 idle turns a game as observation 1.
- The opponent plants 26 / 27 / 23 a game and harvests 23.5 / 22.5 / 25.2 points from its own plants; three stand at the end. The live adjacency inference is **0 wrong on 12,119 plants** across the three packages, ambiguous on 14.4 / 14.4 / 15.2 % of the opponent's. No missing filter; what it buys at the endgame is inside observation 2's ceiling.

## 3. A correction to your 15:47Z ruling's troll timeline — the bench was not an artefact

Your decode read the third troll at median turn 147 from the tooltips' `turn` field and called the bench's 70.5 a bench artefact. Checked game by game against the reconstructed state (first pre-turn state with three of ours), **tooltip `turn` = 2 × game turn − 2 on all 156 games** (ratio 1.95–1.99, difference −2 every time): it is a frame index, one frame per seat. So:

- the dispatcher's third troll lands at **median game turn 75** (quartiles 61 / 75 / 98) — the bench's 70.5 held against real opponents;
- the second troll's "median turn 2 / 16" are game turns 2 and 9; the opponents' third-troll "194" is game turn 97.

The DEAD verdict rests on the rating (14.59 at rank 147 against 18.72 at rank 72) and does not move. The "half a bench artefact" sentence in the ruling and, if it carries the 147, the obituary's timeline in `GRAVEYARD.md` do. The same halving applies to any tooltip-timed reading of the two packages. Your `ladder_read_trolls.py` is right in every other respect; the field's name is the trap.

Bounds kept: a read, no build, no ladder, no platform, no design. Scratch: the three unpacked packages sit in `/data/scratch/claude1-lo/` (81 GB free), removable at your word.

— claude_1
