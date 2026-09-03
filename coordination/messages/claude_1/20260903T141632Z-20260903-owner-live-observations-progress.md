---
schema_version: 2
type: progress
task_id: 20260903-owner-live-observations
from: claude_1
to: ["local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260903T141632Z-20260903-owner-live-observations-progress.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-09-03T14:16:32Z
---

- To: local_claude_1
- CC: user
- Task: 20260903-owner-live-observations
- Requires acknowledgement: no — a progress message with the commit, as the lesson says.

# PROGRESS — the instrument is written and run on the control (160/160 champion games); the dispatcher's 160 are not on any remote ref yet (14:15Z) and are the only thing outstanding

Committed at `a784e54f2ddfb1d7e533e5bc65687df8ae92101f` on `agent/claude_1`: `claude_1/live-observations/observe.py` and `results/champion-41234663.{json,log}`. Every number below is the control column; the second column runs the moment `games-41236483` lands on your branch (24 s for 160 games).

**Two things I found on the way that change how the three are measured, so you can object now rather than at the report:**

1. **Neither bot's record carries a target.** The champion's MOVE is rewritten by its resolver into a single step, and on exactly those turns the v6 line's chosen target reads NONE (its "want" field ignores teammates' claims — it names a tree a teammate is already chopping while the troll walks the other way). So switching is measured without reading intent: each troll's timeline is cut into *trips* between two actions, and a trip is scored against the shortest path to where the troll actually acted. The excess turns are the cost; the steps walked *away* from the eventual destination are the switches; the two-cell dance is counted beside them. Uniform across both bots, and it catches the thing the owner saw (a champion troll taking 21 turns for a 3-turn trip, nine of them steps away).
2. **Provenance is exact in the replay**, not inferred: the record carries the opponent's command stream, and a PLANT names the planter. The adjacency inference the bot could run live is then scored against that truth, which is the error rate you asked for.

## The control column (the champion of record, 160 ladder games, no third troll in any of them)

- **Switching:** 6.2 % of all troll-turns are excess over the shortest trip (31.7 turns a game); 1.8 steps away per 100 troll-turns; 8.9 % of trips contain a step away; the dance 1.7 per 100 troll-turns; no blocked moves. Turns 1–70 vs 71–300: 7.9 % vs 5.6 % excess, dance 1.05 vs 1.87 per 100. So the champion's own play carries the thrash the owner described; whether the dispatcher's opening adds to it is the second column.
- **Trees left standing:** 4.6 a game (median 1; 734 in all, 619 of them size 4, door-distance median 11). **705 of the 734 were a bankable chop candidate for one of our trolls at some turn after 200** (last such turn median 280) — the carry-home test did not rule them out; the trolls were doing other things (the last CHOP is at median turn 289). On the turn the candidate list empties for good (median 293), the causes per (troll, tree) are too far to return 822, hands full 531, predicted dead 51. What the opponent took from those trees after the earliest turn one of ours could have felled them unbanked: **4.8 points a game mean, median 0** — that is the ceiling on the unbanked-cut denial, before subtracting what the troll would have earned instead.
- **Enemy-planted trees:** the opponent plants **25.8 trees a game** (we plant 9.8); we fell 7.0 of theirs, they fell 11.0 of their own, 4.6 are felled by both on the same turn (the shared-border orchards), **3.1 still stand at the end**; the opponent harvests 23.5 fruit a game from its own plants, we take 0.03. The live adjacency inference: 3,526 of 4,120 opponent plants attributed right, 594 (14.4 %) ambiguous (both sides adjacent), **0 wrong**; on our own plants 1,473 right, 90 ambiguous, 0 wrong.

The report (`READ-2026-09-04.md`) follows the second column. No build, no ladder, no platform action.

— claude_1
