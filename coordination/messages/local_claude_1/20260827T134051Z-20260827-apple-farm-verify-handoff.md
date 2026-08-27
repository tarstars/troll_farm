---
schema_version: 2
type: handoff
task_id: 20260827-apple-farm-verify
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260827T134051Z-20260827-apple-farm-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: f875f4a1a3f58ee8b16e18b2a7801cf3b4e33ece
artifact_paths: ["coordination/tasks/20260827-apple-farm-verify.md", "coordination/tasks/20260827-apple-farm-instrument.md", "local_claude_1/apple-farm/make_apple_farm.py", "local_claude_1/apple-farm/fixtures_diff.py", "local_claude_1/apple-farm/smoke.py", "local_claude_1/apple-farm/champion-apple-farm-v6-instrument.rs.sha256", "local_claude_1/apple-farm/results/build.json", "local_claude_1/apple-farm/results/fixtures.json", "local_claude_1/apple-farm/results/smoke.json", "cgauto/submissions/candidate-apple-farm-v6-instrument.rs", "cgauto/submissions/candidate-apple-farm-v6-instrument.rs.sha256", "readable/diffs/apple-farm.diff", "readable/reports/candidate-apple-farm-v6-instrument.round-trip.json", "coordination/BOARD.md"]
created_utc: 2026-08-27T13:40:51Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260827-apple-farm-verify
- Requires acknowledgement: yes — a charter (board row 0-5)

# handoff: 0-5 — re-run the apple-farm build, its bed and its smoke on `main`, and say whether the bytes on the ladder are the bytes the diff says

Card: `coordination/tasks/20260827-apple-farm-verify.md`. Context in one line: the owner's next one-variable experiment — the champion of record plus one rule: if a grass cell touching our shack also touches water, the starting troll plants an apple there on turns 1–3 (a water-side apple regrows a fruit every 2 turns), runs the normal opening, and once the second troll is trained harvests it to the end, HARVEST and DROP alternating without moving; no own troll ever fells that tree — is on the ladder as submission `41203549` (13:34:48Z) for one hour. I built it myself, so it has only agreed with itself. The ladder reading (≥ 14:35Z) does not wait for you.

**What to run**, on a clean checkout of `main` at `f875f4a1a3f58ee8b16e18b2a7801cf3b4e33ece` or later:

1. `python3 local_claude_1/apple-farm/make_apple_farm.py` — regenerates the arm from the champion's diagnostics arm (`local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs`, sha256 32172393…) and the readable champion (`readable/denial-off-champion.rs`, sha256 4ce3d1e8…) with four pure insertions applied identically to both, compiles, compacts, round-trips. Expected: arm sha256 `82c8ddd1347c8016…` (the full value is the sidecar `local_claude_1/apple-farm/champion-apple-farm-v6-instrument.rs.sha256`), submission sha256 `8c6bc206417c6d22b593372ce42e74ce5698646c1f8a860073f349a2a082708c` (66,082 bytes), +120 / −0. It overwrites tracked files; `git status` must be clean afterwards.
2. `python3 local_claude_1/apple-farm/fixtures_diff.py` — expected: plays 34/34, differs from the champion on 2/34 (OSC-026 first divergence turn 3, OSC-030 turn 1), deterministic 34/34, compacted == arm 34/34, telemetry errors 0.
3. `python3 local_claude_1/apple-farm/smoke.py --maps 24 --turns 300 --seed 0` — full 300-turn games on 24 real ladder maps that have a water-side door (from `data/processed/maps.jsonl`; if your checkout lacks it, the script falls back to the main checkout's copy at `/home/tarstars/prj/troll_farm/data/processed/maps.jsonl` — say so if neither is reachable from the VM and stop at step 2), arm vs the resident on the same map and scripted opponent. Expected: mechanics ok 24/24 (planted on turn 3 everywhere, no own CHOP on the farm cell), and the own-score sum arm − resident — mine was +2831; report yours as a fact.
4. Read `readable/diffs/apple-farm.diff` (+120 lines, nothing removed) and say in one sentence whether anything in it can make an own troll fell the farm tree or plant on the farm cell while the farm troll is away — or "nothing".

**Return** one verdict message: REPRODUCED or NOT REPRODUCED, with the two hashes, the bed's five counts, the smoke's two numbers, and your one sentence. No edits to the generator; if something differs, the first differing line and stop. Budget: one run of each, one message, today. No Arena, no builds of your own.
