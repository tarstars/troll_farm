---
schema_version: 2
type: handoff
task_id: 20260902-endgame-move-gap
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260902T093614Z-20260902-endgame-move-gap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-09-02T09:36:14Z
artifact_ref: agent/claude_1
artifact_commit: 447ff1d95954e14024c4c4603d6cf2e14e6ef716
artifact_paths: ["claude_1/endgame-gap/READ-2026-09-02.md", "claude_1/endgame-gap/phase_mix.py", "claude_1/endgame-gap/champ_endgame.py", "claude_1/endgame-gap/idle_read.py", "claude_1/endgame-gap/idle_feasible.py", "claude_1/endgame-gap/top4_tables.py", "claude_1/endgame-gap/phase-mix.json", "claude_1/endgame-gap/champ-endgame.json", "claude_1/endgame-gap/idle-read.json", "claude_1/endgame-gap/idle-feasible.json", "claude_1/endgame-gap/top4-tables.json", "coordination/BOARD.md"]
---

- To: local_claude_1
- CC: codex_1, user
- Task: 20260902-endgame-move-gap
- Requires acknowledgement: yes — the card's one review round; then the paragraph on the board and the line's closure

# HANDOFF — Track E read delivered: the endgame MOVE gap is real, late-only, and not idle production; no candidate rule; close into Track P

The report is `claude_1/endgame-gap/READ-2026-09-02.md` at `447ff1d9`, a day early. Sources: the whole
per-turn corpus in place (hash `1e0ea236…` checked by the script before reading; 13.3 M turn rows) for
the top four, and the champion of record's 160 collected games replayed through the fits' exact
reconstructor (0 inventory or carry mismatches; the final scores equal the replays' own) for ours.

**1. The mix by phase.** Per troll-turn our champion moves as much as the top four until turn 250
(0.50–0.56 against their 0.41–0.58); in turns 251–300 it drops to **0.17** while they stay at
**0.37–0.62** and the opponents in our own games at 0.51. So row T-1's 8-vs-32 is per game (ours 15.5
MOVE in the last fifty, median 12; theirs 68), per troll and per turn, and **a late-game gap only**; the
roster (2.00 trolls against 2.86–3.43) multiplies it. Not an emission artefact: the reconstruction reads
positions. The corpus's own copy of our lineage (`tass`, 7,719 late game-seats: 2.02 trolls, 0.33 MOVE a
turn, 9 % idle turns) agrees with the collected games.

**2. What our trolls do instead** (8,930 late troll-turns): CHOP 37 %, **no command 21 %**, MOVE 14 %
(+2.6 % oscillating), DROP 10 %, the one-wood swap's PLANT/PICK 16 %, HARVEST 0. The idle turns: a free
tree reachable but unfinishable 33 %, only enemy-guarded trees 25 %, the partner on the only tree 22 %,
no tree at all 20 %; 53 % of them fall in turns 291–300, and **84 % are terminal** — no reachable tree
could be felled or a fruit banked before turn 300. Three games to open are in the report (e.g. 900573896:
both trolls wait fifty turns while four enemy trolls surround the last plum). Two facts about the bot
settled on the way: it never harvests, and it never trains a third troll.

**3. The points at stake.** 64 of 160 games end before turn 251 because no tree is left (we win 43).
In the 96 that run on: when we lead at 250, the last fifty are a wash (+31 vs +34; we win 39 of 43);
when we trail, **+34 vs +80** (we win 3 of 53). The deficit decomposes as **roster ×0.70 · idleness
×0.85 · output per acting troll-turn ×0.93**. The top four's own last-fifty gains: delineate +123 (with
2.9 trolls, 17.6 trees kept on the map), MSz +98, norxondor +84, Bubaptik +78.

**4. Candidate rule: none.** Everything an endgame rule could recover is bounded at about **six points
a game** (3.3 from trees an idle troll could have felled and nobody took, 0.3 fruit, 2.5 from co-chop
wood duplication — the engine's last-wood rule, `engine.rs:604–627`), one eighth of the 46-point
deficit, on a lost map in the last ten turns. Real gap, wrong layer: the third troll and a map kept
alive, which is Track P's macro layer. **Recommendation: close Track E as "real, not idle production";
carry two endgame signatures to Track P's loss read — MOVE per troll-turn in 251–300 (ours 0.17, the
field 0.37–0.62) and tree-size units standing at the end (ours median 4).**

Not done, said plainly: the top four's own idle *causes* need their raw replays, which are not on the
VM (16 of 4,128 present); their idle *share* is read from the exact per-turn tables instead (delineate
3.8 %, norxondor 0 %, MSz 13 %, Bubaptik 3.8 %). Board row E-1 updated in the artifact commit. Scratch:
`/data/scratch/claude1-champ-41202036/` (51 MB, the 160 replays as files for the reconstructor; delete
at will). No build, no ladder, no platform action.
