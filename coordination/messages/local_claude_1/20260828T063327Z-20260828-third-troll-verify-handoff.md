---
schema_version: 2
type: handoff
task_id: 20260828-third-troll-verify
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260828T063327Z-20260828-third-troll-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260828T061320Z-20260828-third-troll-verify-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 9d70455300b12972a3fd5acc3dd0373eed1a1143
artifact_paths: ["coordination/tasks/20260828-third-troll-verify.md", "local_claude_1/third-troll/make_three_heroes.py", "local_claude_1/third-troll/make_third_troll.py", "local_claude_1/third-troll/fixtures_diff.py", "local_claude_1/third-troll/smoke.py", "local_claude_1/third-troll/results/build-heroes.json", "local_claude_1/third-troll/results/fixtures-heroes.json", "local_claude_1/third-troll/results/smoke-heroes.json", "readable/diffs/three-heroes.diff"]
created_utc: 2026-08-28T06:33:27Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260828-third-troll-verify
- Requires acknowledgement: yes — the re-charter of row 0-7 (supersedes my 20260828T061320Z-20260828-third-troll-verify-handoff.md)

# handoff: 0-7 re-chartered — reproduce THREE HEROES, not (a)

The owner retired (a) from the ladder at 06:2xZ ("extremely low rating and it's quite obvious why — the second troll chops down the trees with resources for the third troll") and approved a second design: the second troll gets harvest power 1; after it both trolls collect the third troll's bill and NOBODY CHOPS until the 2/3/0/3 third troll is trained or unreachable (a missing fruit with no living tree of its kind, or fewer than 100 turns left). Built as **three heroes** — `local_claude_1/third-troll/make_three_heroes.py` (the nine replacements of `make_third_troll.py` plus seven, stacked). It is queued on the VM to go up after the champion's hour (~07:27Z). Your verdict decides whether its second round stays in the queue.

**What to run**, on a clean checkout of `main` at `9d704553` or later — the card `coordination/tasks/20260828-third-troll-verify.md` has the exact commands and numbers:

1. `python3 local_claude_1/third-troll/make_three_heroes.py` — arm sha256 `14b2f3906cfd6c2a…`, submission sha256 `2abb9fc29c574f33…` (65,508 bytes), +128 / −31; `git status` clean (delete the untracked `results/build-v6.json` it leaves).
2. the bed with absolute `--arm/--submission/--out` (card step 2) — plays 34/34, differs 6/34, deterministic 34/34, compacted == arm 34/34, telemetry 0, a third troll in ['OSC-010'].
3. the smoke with `--arm local_claude_1/third-troll/champion-three-heroes-v6-instrument.rs --out local_claude_1/third-troll/results/smoke-heroes.json` — PASS 24/24, a third troll in 20/24, median turn 111, funding median 106, 4 × "bill never paid by turn 200", stalled [], own-score sum −1 (+127 on the 20).
4. Read `readable/diffs/three-heroes.diff` (+128 / −31): one sentence — can anything in it let an own troll CHOP while the bill is being collected, train a fourth troll, or keep collecting after a fruit of the bill has no living tree left — or "nothing".

**Return** one verdict message: REPRODUCED or NOT REPRODUCED, with the two hashes, the bed's counts, the smoke's numbers, and your one sentence. Dead means: the first differing line, and stop; no edits to the generators. If NOT REPRODUCED: remove `three-heroes-r2` from `local_claude_1/ladder-queue/queue.json` in the VM checkout `/home/tarstars/prj/troll_farm` and say so. Budget: one run of each, one message, today. No Arena. The (a) steps in the card are for the record only — do not run them.
