---
schema_version: 2
type: handoff
task_id: 20260828-third-troll-verify
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260828T061320Z-20260828-third-troll-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 91c505842115d506d6ac09c6ce337f5480c770fa
artifact_paths: ["coordination/tasks/20260828-third-troll-verify.md", "local_claude_1/third-troll/make_third_troll.py", "local_claude_1/third-troll/fixtures_diff.py", "local_claude_1/third-troll/select_equivalence.py", "local_claude_1/third-troll/smoke.py", "local_claude_1/third-troll/smoke-maps-seed0.jsonl", "local_claude_1/third-troll/results/build.json", "readable/diffs/third-troll.diff"]
created_utc: 2026-08-28T06:13:20Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260828-third-troll-verify
- Requires acknowledgement: yes — a charter (board row 0-7)

# handoff: 0-7 — reproduce the third troll's build, bed, smoke and select-equivalence (the bot is already on the ladder)

The owner's next one-variable experiment is the third troll: the champion of record plus one change — after the second troll, both trolls collect the bill of a 2/3/0/3 lumberjack and train it the turn it is affordable (card `coordination/tasks/20260828-third-troll.md`). It is on the ladder since 05:49:18Z as `41206542` on the owner's word, before your verdict (the owner is offline for 8 hours; a ladder queue on the VM runs the next items — do not touch `local_claude_1/ladder-queue/` except as the card says). Your verdict decides whether its second round stays in the queue.

**What to run**, on a clean checkout of `main` at `91c50584` or later — the card `coordination/tasks/20260828-third-troll-verify.md` has the expected numbers in full:

1. `python3 local_claude_1/third-troll/make_third_troll.py` — arm sha256 `30bf84226f26b82b…`, submission sha256 `89493fa0d68e1dea…` (65,342 bytes), +123 / −29; `git status` clean afterwards. Then `python3 local_claude_1/third-troll/make_third_troll.py 2202` — the 2/2/0/2 variant: submission sha256 `684104f136f93ac6…`, +123 / −29, `git status` clean.
2. `python3 local_claude_1/third-troll/fixtures_diff.py` — plays 34/34, differs 27/34, deterministic 34/34, compacted == arm 34/34, telemetry 0, arm trained 1/34 (champion 1/34), a third troll in [], wrong spec [], more than three [].
3. `python3 local_claude_1/third-troll/select_equivalence.py` — PASS, identical play on 58/58.
4. `python3 local_claude_1/third-troll/smoke.py --records local_claude_1/third-troll/smoke-maps-seed0.jsonl` — mechanics ok 23/24 (the 24th, `c84154d29ea19fbc`, both bots idle on a bare map after turn 200; report the numbers as they come), a third troll in 5/24, median turn 158, funding median 144, 19 × "bill never paid by turn 200", own-score sum +497 (+82 on the 5).
5. Read `readable/diffs/third-troll.diff` (+123 / −29): one sentence — can anything in it train a FOURTH troll, train the third before the second, train it in the last 100 turns, or leave a troll without a command list — or "nothing".

**Return** one verdict message: REPRODUCED or NOT REPRODUCED, with the three hashes, the bed's counts, the equivalence count, the smoke's numbers, and your one sentence. Dead means: a hash, a count or a number that differs — the first differing line, and stop; no edits to the generator. If NOT REPRODUCED: also remove the item `third-troll-2303-r2` from `local_claude_1/ladder-queue/queue.json` in the VM checkout `/home/tarstars/prj/troll_farm` (the runner reads it there) and say so. Budget: one run of each, one message, today. No Arena. `rustc` is at `~/.cargo/bin/rustc` on the VM; the scripts need it on PATH.
