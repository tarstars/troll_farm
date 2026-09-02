---
schema_version: 2
type: handoff
task_id: 20260902-endgame-move-gap
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/local_claude_1/20260902T082010Z-20260902-endgame-move-gap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 615c87e07603f977d35b5e9d082ca28e697224aa
artifact_paths: ["coordination/tasks/20260902-endgame-move-gap.md", "coordination/BOARD.md"]
created_utc: 2026-09-02T08:20:10Z
---

- To: claude_1
- CC: codex_1, user
- Task: 20260902-endgame-move-gap — Track E, a one-day read
- Requires acknowledgement: yes — a dated deliverable; acknowledge with your start time (this comes
  second in your queue, behind the head-to-head panel instrument of Track P).

# HANDOFF — what our trolls do in the last fifty turns that the top bots' trolls do not

The card is `coordination/tasks/20260902-endgame-move-gap.md`; read it whole. In one breath: row
T-1 (`codex_1/top10/field-comparison-2026-08-26.md`) left one gap unexplained — **our bot issues
about 8 MOVE commands in the endgame where the strong bots issue 32–38** — and our oldest known
weakness is the late game (we lead early and are out-produced late). If our trolls stand, wait or
repeat a low-value action in turns 251–300 while theirs keep working, that is production left on
the table and the cheapest kind of fix; if the gap is an artefact of carry or geometry, the read
says so and the line closes.

**Evidence, nothing new played:** the per-turn command corpus `data/processed/turns.jsonl.gz`
(row T-2; the top four are agents `6479768` delineate, `6480540` norxondor_gorgonax, `6479460` MSz,
and Bubaptik per `local_claude_1/reconstructions/profiles/`), the champion of record's collected
ladder games with telemetry `local_claude_1/denial-ablation/games-41202036/` (160 games), the exact
per-turn reconstruction of row R-1 (`local_claude_1/reconstructions/fits/`) for positions, loads
and scores.

**Deliverable** `claude_1/endgame-gap/READ-2026-09-02.md`, one page plus tables, by
**2026-09-04 12:00Z** (after P-0): (1) the command mix by phase (turns 1–100, 101–200, 201–250,
251–300) for our champion and each of the four, per troll per turn, and whether the 8-vs-32 gap is
per game, per troll or per turn, late-game or all-game; (2) what our trolls do instead in turns
251–300, with three example games (id, turn, cell) the owner can open; (3) the points at stake —
our score gained in turns 251–300 against the opponent's, over the 160 games, split by whether we
led at turn 250, and the same for the top four in their games; (4) one candidate rule in plain
words, judged from game state down, with the expected size of the effect and how the local panel
would read it — or "artefact, close". Handoff ack-required to me, cc codex_1 (it may matter for the
port's endgame).

Dead if the corpus rows cannot separate phases or command types for the top four — then the report
names the missing field and stops. No build, no ladder, no platform action.
