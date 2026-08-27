---
schema_version: 2
type: handoff
task_id: 20260827-the-floor-verify
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260827T180640Z-20260827-the-floor-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 30afd10aa2257f9f09333214c0dac5f091a70575
artifact_paths: ["coordination/tasks/20260827-the-floor-verify.md", "coordination/tasks/20260827-the-floor.md", "local_claude_1/the-floor/make_the_floor.py", "local_claude_1/the-floor/fixtures_diff.py", "local_claude_1/the-floor/smoke.py", "local_claude_1/the-floor/smoke-maps-seed0.jsonl", "local_claude_1/the-floor/champion-the-floor-v6-instrument.rs.sha256", "local_claude_1/the-floor/results/build.json", "local_claude_1/the-floor/results/fixtures.json", "local_claude_1/the-floor/results/smoke.json", "cgauto/submissions/candidate-the-floor-v6-instrument.rs", "cgauto/submissions/candidate-the-floor-v6-instrument.rs.sha256", "readable/diffs/the-floor.diff", "readable/reports/candidate-the-floor-v6-instrument.round-trip.json", "local_claude_1/second-troll-census/README.md", "coordination/BOARD.md"]
created_utc: 2026-08-27T18:06:40Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260827-the-floor-verify
- Requires acknowledgement: yes — a charter (board row 0-6)

# handoff: 0-6 — re-run the floor's build, its bed and its smoke on `main`, and say whether the bytes that will go on the ladder are the bytes the diff says

Card: `coordination/tasks/20260827-the-floor-verify.md`. Context in one line: the owner's next one-variable experiment ("let's build the_floor") — the champion of record with one change: **the second troll is never weaker than speed 2, carry 2, chop 2** (harvest 0 as before); the bot waits for it, and from turn 35 takes the strongest floored troll it can afford or keeps waiting for the basic 2/2/0/2. Why: the second-troll census (`local_claude_1/second-troll-census/README.md`) — the strong bots buy the same 2/2/0/2 troll, later and never weaker; we field a weaker one in 37–45 % of games and lose those twice as often within a batch. I built it myself, so it has only agreed with itself. It goes on the ladder after the apple farm's sixth reading (~21:05Z); a NOT REPRODUCED before that stops the submission.

**What to run**, on a clean checkout of `main` at `30afd10aa2257f9f09333214c0dac5f091a70575` or later:

1. `python3 local_claude_1/the-floor/make_the_floor.py` — regenerates the arm from the champion's diagnostics arm (`local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs`, sha256 32172393…) and the readable champion (`readable/denial-off-champion.rs`, sha256 4ce3d1e8…) with five replacements applied identically to both, compiles, compacts, round-trips. Expected: arm sha256 `75afaf8bd1d380fc…` (the full value is the sidecar `local_claude_1/the-floor/champion-the-floor-v6-instrument.rs.sha256`), submission sha256 `31cd23c021f184b0…` (sidecar next to `cgauto/submissions/candidate-the-floor-v6-instrument.rs`; 63,791 bytes), +17 / −23. It overwrites tracked files; `git status` must be clean afterwards. (The generator also prints `rustfmt --check: NOT clean` for the edited readable — inherited: the base readable is not clean under the installed rustfmt either; not a finding.)
2. `python3 local_claude_1/the-floor/fixtures_diff.py` — expected: plays 34/34, differs from the champion on 2/34 (OSC-010 first divergence turn 13, OSC-032 turn 49), deterministic 34/34, compacted == arm 34/34, telemetry errors 0, "below the floor: []".
3. `python3 local_claude_1/the-floor/smoke.py --records local_claude_1/the-floor/smoke-maps-seed0.jsonl` — 24 real ladder maps with their draws and opponent profiles (a 64 KB slice; it replays my corpus run identically, so the 53 MB corpus is not needed). Expected: PASS 24/24 (the arm trains in every game, never below 2/2/0/2), the resident below the floor on 11/24, training turn median arm 30 vs resident 11, own-score sum arm − resident +149 (a fact, not a verdict).
4. Read `readable/diffs/the-floor.diff` (+17 / −23) and say in one sentence whether anything in it can train a troll weaker than speed 2 / carry 2 / chop 2, or stop the bot from ever training — or "nothing".

**Return** one verdict message: REPRODUCED or NOT REPRODUCED, with the two hashes, the bed's counts, the smoke's numbers, and your one sentence. No edits to the generator; if something differs, the first differing line and stop. Budget: one run of each, one message, today. No Arena, no builds of your own.
