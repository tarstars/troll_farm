---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-1-hold
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260825T113500Z-20260825-dance-cure-candidate-1-hold-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 5d51b8c7df958383a6a1997e6bae74193e81fee5
artifact_paths: ["local_claude_1/cure1/g2-games/games-agent6659743-submission41192036.jsonl.gz", "local_claude_1/cure1/g2-games/battle-index-agent6659743-submission41192036.json", "local_claude_1/cure1/g2-games/manifest.json", "local_claude_1/cure1/g2-read-2026-08-25.md", "cgauto/submissions/candidate-hold-v1-instrument.rs"]
created_utc: 2026-08-25T11:35:00Z
---

- To: claude_1
- CC: codex_1, user, chatgpt_1
- Task: 20260825-dance-cure-candidate-1-hold
- Requires acknowledgement: yes — this is the G-2 package your grading card waits on

# G-2 PACKAGE HANDOFF — 160 real ladder games of the Candidate 1 instrument, collected before any resubmission, identity clean. Grade it.

`agent/local_claude_1@5d51b8c7`, five paths, all present at that commit.

## What was played

| | |
|---|---|
| arm | `cgauto/submissions/candidate-hold-v1-instrument.rs`, sha256 `cc4b308705883f10192065dd205a36eb78baee3c1068a0697131b791f3d46e9b` = your `arm-manifest.json` instrument (`agent/claude_1@a4a63bad`) |
| submission / agent | **41192036 / 6659743**, submitted 2026-08-25T10:38:12Z (`api_submit_once`, expected hash verified, 1 mutation call) |
| off-ladder check first | `TestSession/play` game `900326333`: 300/300 turns decoded by `narrate4`, 0 failures, hold fired 4×, `pz` ≤ 2, longest line 125, 0 of our fragments on the opponent's seat — PASS |
| games | **160**, the whole burst (window 160/160 ours at 11:30Z); first collection at 155 (11:20Z), top-up to 160 (11:30Z) |
| package | `games-agent6659743-submission41192036.jsonl.gz`, **6,308,554 bytes, sha256 `050d1ceb65ba1f03e67065f311920cb4aab19eb0e6564a1f285477d2dc5c6a38`**, sanitised by `cgauto/export_agent_replays.py` via `collect_submission_games.py`; `manifest.json` carries the same digest |
| score (informational, not a G-2 criterion) | 21.8 / rank 39 at 11:30Z, unmatured |

## Identity checks I ran on the final package (verify, do not trust)

- forbidden-key sweep over every game: **0 hits**;
- our seat resolved from each replay's `agents` array by `agentId == 6659743` in **160 of 160**
  games (70 seat 0, 90 seat 1) — never from the battle listing's position;
- every own-seat turn carries exactly one `MSG NARRATE v4` fragment that **decodes with 0
  failures: 42,070 of 42,070 turns**;
- **0** `NARRATE` fragments on the opponent's seat in any game.

I did **not** compute branch counts, holds, `R_pos`, classes or any graded number — those are the
grade, and the grade is yours; I have not looked.

## The grade (the contract of `20260825T103500Z`, restated)

Accepted attribution pipeline unmodified (adapter → `detect_d1` → r3 classification with `mech`),
plus per game: the v4 branch census (`H`, `R`, `L`, `P`, `W`, `N`), holds followed by progress,
**this read's own scope-active share** (codex_1's requirement — the panel's 228/240 does not
transfer), idle-with-work per troll (`H` + `W`), D-3, F7 endings, D-1 rows split transient vs
permanent by `r=`, and `R_pos` by your pre-committed script with the `R_pos` ↔ `r=R` crosswalk
published as a finding. Graded against: **(a)** holds fire and are followed by the dancer's
progress, F7 `DANCER_PROGRESS` share ≥ 52 of 80; **(b)** `R_pos` ≤ **3.8386** per 1,000 own
troll-turns (the accepted bar); **kill:** idle-with-work > 1.5 %, D-3 > 0, long-stall share of
games above the champion's, any P1/P2 row migrating to a parked or stalled shape. Hand off with
the full commit and paths; codex_1 runs one fresh-archive execution check and verifies the package
identity against this manifest.

The read is spent; the second pre-authorized action (the G-3 block, candidate arm vs champion)
starts only if your grade passes and after I surface it to the owner.

Deferrals: none.
