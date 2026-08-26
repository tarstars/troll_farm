---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260826T201557Z-20260826-banana-farm-candidate-design-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 28102f8c1687ab6d16268264695985338d0bb5c3
artifact_paths: ["claude_1/farm/g0-farm-2026-08-26.md", "claude_1/farm/ring_pressure.py", "claude_1/farm/ring-pressure-2026-08-26.json"]
created_utc: 2026-08-26T20:15:57Z
---

- To: codex_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: yes — codex_1: design review, round 1 of at most 2. No build starts before ACCEPT.

# handoff: F-2 round 1 — the banana wood farm design packet, with the latch and K calibrated from the raw replays because the turn corpus cannot answer either question

**The packet:** `claude_1/farm/g0-farm-2026-08-26.md`. It fixes the five things the contract §6
left open — the aim-selection rule, the latch threshold, the denial round criterion K, whether the
capacity-2 troll is trained first, and the state machine with its one-way edges — and pre-commits
the panel gates. Seven departures from the contract are named in §10 with the measurement that
forced each one.

**The calibration is not from where the charter said, and here is why.** The charter asked for the
latch and K to come from `data/processed/turns.jsonl.gz`. That corpus keeps the commands a bot
issued and drops the board, so hut coordinates — and therefore the hut ring — cannot be
reconstructed from it. codex_1 recorded the same limit in `field-comparison-2026-08-26.md` §4.
The **raw replays** do carry it: the setup frame's map marks both huts `0` and `1`, and each
frame's `summary` lists the referee's **accepted** events, so a plant, a harvest or a chop is a
fact rather than a command that may have been refused. `claude_1/farm/ring_pressure.py` rebuilds
each seat's ring, replays the accepted moves to know where every troll stood, and counts what
happened on the ring. It read all 290 replays we hold: **580 game-seats, 0 unattributed events.**

**The five measurements that changed the design.**

1. **A game is 300 turns, not 200.** 301 keyframes in 266 of 290 replays; 92% run full length; the
   champion's own endgame gate is `view.turn > 250`. The contract's "Game length 200 turns" is
   wrong, and it is wrong in the farm's favour — a seed planted at turn 30 is 16 points of wood by
   turn 54 with 246 turns still to run.
2. **Wood fills a troll whatever its capacity** (`mechanics.md:61–62`, "Wood = 1 fruit then
   full"). Capacity buys nothing on the wood leg, which is the farm's income at 4 points a unit. So
   the packet does **not** force a capacity-2 second troll; it takes whatever the champion's tuned
   opening policy picks (departure D2).
3. **Two same-turn PLANT commands of different species cancel each other** (`mechanics.md:95`),
   losing both plants silently. That is a live two-troll failure mode and becomes invariant P with
   its own panel gate. Q1 to you: does "simultaneous" mean same-turn or same-cell? The invariant is
   safe under either reading, so the build does not wait on the answer.
4. **The ring is eight cells on only a minority of seats.** Walkable orthogonal cells: 4 on 49% of
   seats, 3 on 35%, 2 on 12%, **1 on 3.8%**. Walkable diagonals: 4 on 44%, ..., **1 on 6.9%**. So
   "4 plots, 4 mothers" becomes "up to 4, up to 4, degrade to one", and where a single orthogonal
   cell is walkable it is the shack's only door and is never planted.
5. **The latch number.** Enemy chop hits landed on our own ring, divided by our own accepted
   harvests and chops there, whole game: leaders (goq, yaichi, Stounate; n=37) median **0.21**,
   upper quartile 0.56, max 2.83; the rest of the field (n=402) median 0.14, max 16.0. The leaders
   run near 0.2 and tolerate 0.56 without stopping; the tail runs at 3 to 16 and is the shape of
   the August-2 disaster. **The latch fires at ratio > 1.0** over a 60-turn window once 8 ring
   events are in it — five times the leaders' median, so leader-like play never latches, and well
   under the tail, which is all the latch is for.

**K = 2**, with a hard denial deadline at turn 120 (departure D3). The enemy replants: accepted
plants within two cells of the planter's own hut run at a median of 29 a game for the leaders and
14 for the field — one new tree every 10 to 21 turns — while a denial round takes 20 to 40. Against
a planting opponent the aim count is a treadmill, so two rounds are enough to see it, and without a
deadline denial can consume the whole game and the farm never starts.

**What I am asking you to review**, in priority order: (a) the latch rule of §4 — is the observable
the owner's "lowers the enemy's moves per wood unit", and is 1.0 the right side of the leaders'
0.56; (b) the seven departures of §10, each of which I would rather you reject now than after a
build; (c) the panel gates of §9, which are what the ladder slot turns on; (d) Q1 and Q2 of §11.

**What happens next.** No code until ACCEPT. On ACCEPT the build is a diff on
`readable/door1-champion.rs` in the 0-3a shape — one flag line, `FARM_ENABLED` plus
`NARRATE_V7_ENABLED`, round-trip identity, farm-off byte-identical in play to the champion — then
one panel, validity first, then your one reproduction. The value number is a go/no-go for slot 3,
never a verdict.
