---
schema_version: 2
type: handoff
task_id: 20260902-cheap-third-troll
from: claude_1
to: ["local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260903T042300Z-20260902-cheap-third-troll-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 54786b02acc8c58f7dd4bd142756cbdcd7e24ecf
artifact_paths: ["claude_1/cheap-third-troll/READ-2026-09-03.md", "claude_1/cheap-third-troll/replay_read.py", "claude_1/cheap-third-troll/detour_cost.py", "claude_1/cheap-third-troll/paper.py", "claude_1/cheap-third-troll/games-41202036.json", "claude_1/cheap-third-troll/games-41230202.json", "claude_1/cheap-third-troll/detour-41202036.json", "claude_1/cheap-third-troll/detour-41230202.json", "claude_1/cheap-third-troll/paper-2026-09-03.json"]
created_utc: 2026-09-03T04:23:00Z
---

- To: local_claude_1
- CC: user
- Task: 20260902-cheap-third-troll
- Requires acknowledgement: yes — step 1's deliverable; the ruling (the on-paper death, or a step 2) is yours.

# HANDOFF — the read: the cheap third troll is dead on paper

**Deliverable:** `claude_1/cheap-third-troll/READ-2026-09-03.md` at the pin above — one page for the owner, the five
tables behind it, the three scripts and their JSON beside it. Started 04:02Z, delivered within the day; nothing
built, played, submitted or sent.

**The answer.** The champion never holds the cheap bill: after its second troll the bank has a median 1 plum,
0 lemons, 5 apples, 7 bananas, 0 iron, and the 1/1/0/1 bill (3/3/2/3) is short in **319 of 319** games, by a median
of 6 items. Two facts of the bot make the shortfall dear. Every trained shape has harvest power 0, so the fruit is
the **starter's** job alone, and it carries one item: a fruit is a round trip, not a one-turn pickup. And after
training the champion banks nothing at all for the rest of the game (0.03 items a game); it spends the bank as
swap seeds — 9.8 a game, **81 % of its plums and lemons**, felled as size-1 trees for 44 points a game — so a banked
plum is worth up to 4 points to it, not 1.

**The numbers.** Trip model on each game's exact post-training board (calibrated against the champion's own 203
collecting openings: actual − model median +1 turn): the fruit takes the starter a median **37 turns** (q25–q75
26–55) while the trained troll mines the iron in 9; only 107 of 319 games get the bill inside 30 turns. Wood forgone
**11.0 points** [10.4, 11.6] — sixteen two-troll chopping turns, under the card's thirty. Fruit 8 points at face value,
25.5 as seeds. Earnings: a 1/1/0/1 banks 0.042 wood a troll-turn (our starter's own rate; 0.28 of our 2/2/0/2's
0.150; carry 1 binds), from turn 52 for 203 turns: **30.0 points** [28.2, 31.9] (ceiling 36.9 uncontested, floor 20.4
as a share shift on the 108 wood units felled after it arrives).

| design | net, fruit at face value | net, fruit as the seeds it would have been |
|---|---:|---:|
| A1 strong first, then the cheap bill (third troll at turn 52) | +11.0 [9.2, 13.0] | −6.5 [−8.4, −4.6] |
| A2 cheap troll at turn 1 (every draw affords it), strong troll 47 turns late | −7.0 [−10.0, −4.1] | −24.5 [−27.5, −21.6] |
| B30 A1 only when the wall ≤ 30 turns (fires 107/319) | +5.1 [3.8, 6.4] | −0.8 [−1.9, +0.2] |

On the win indicator A1 is +7 games of 319 at face value and −28 at the seed value; B30 +6 / −9.

**Recommendation: no build** — the read's own condition, met on the reading I believe: the earnings cover the bill
only when its fruit is priced at face value, and the 81 % swap rate is measured. The one variant that loses under
neither reading (B30) is worth +5 to −1 a game in a third of the games, under the panel's resolution. Your
expectation was right in shape; the collecting is slower than 25 turns because one troll harvests with carry 1,
and the fruit is dearer than its face value because of the swap. Two doors the read found, both other cards: a
second troll with harvest 1 (one apple more) makes the fruit a two-troll job; the referee prices bananas at zero
for training, so the seven bananas the champion holds buy nothing — a talent that drew on bananas would be free.

**Verification by execution, in order:** `replay_read.py --raw DIR --agent ID --out` on the two scratch replay dirs
(written from the two `games-*.jsonl.gz`; ~35 s a batch), `detour_cost.py` the same way, then `paper.py` — its
printed summary equals `paper-2026-09-03.json`. Expected: bill short 319/319, wall median 37, A1 net +11.01 / −6.51.

Sent 2026-09-03; no queue, ladder, platform or network action taken.
