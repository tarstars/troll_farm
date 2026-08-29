---
schema_version: 2
type: handoff
task_id: 20260828-third-troll-verify
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260828T091836Z-20260828-third-troll-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260828T063327Z-20260828-third-troll-verify-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 4ccb6f00a1d10c1ddead0bcfdc87d0b87f0daac5
artifact_paths: ["coordination/tasks/20260828-third-troll-verify.md", "local_claude_1/third-troll/make_orchard.py", "local_claude_1/third-troll/make_three_heroes.py", "local_claude_1/third-troll/make_third_troll.py", "local_claude_1/third-troll/fixtures_diff.py", "local_claude_1/third-troll/smoke.py", "local_claude_1/third-troll/results/build-orchard.json", "local_claude_1/third-troll/results/fixtures-orchard.json", "local_claude_1/third-troll/results/smoke-orchard.json", "readable/diffs/orchard.diff"]
created_utc: 2026-08-28T09:18:36Z
---

- To: codex_1
- CC: claude_1, user, chatgpt_1
- Task: 20260828-third-troll-verify
- Requires acknowledgement: yes — the re-charter of row 0-7 (supersedes my 20260828T063327Z-20260828-third-troll-verify-handoff.md)

# handoff: 0-7 re-chartered again — reproduce THE ORCHARD (three heroes is superseded)

Three heroes read 11.7 and 12.0 on the ladder (the same floor as (a)); the owner designed the next step — an orchard of four lemons and two plums at the gate of our shack farthest (on foot) from the enemy, planted by the starting troll after the second troll is trained and protected from our own axes until the third troll, plus the dance fix — and it is built as **the orchard** (`local_claude_1/third-troll/make_orchard.py`, stacked on three heroes' sixteen replacements). It goes up on the VM queue at ~09:56Z. Your verdict decides whether its second round stays in the queue. Do not run the three-heroes or (a) steps (for the record only in the card).

**What to run**, on a clean checkout of `main` at `4ccb6f00` or later — the card `coordination/tasks/20260828-third-troll-verify.md` has the exact commands and numbers:

1. `python3 local_claude_1/third-troll/make_orchard.py` — arm sha256 `e6dd87cce442047d…`, submission sha256 `8e0c0244a05abd3f…` (69,477 bytes), +313 / −32; `git status` clean.
2. the bed with absolute `--arm/--submission/--out` (card step 2) — plays 34/34, differs 11/34, deterministic 34/34, compacted == arm 34/34, telemetry 0, arm trained 2/34, a third troll in ['OSC-010'].
3. the smoke with `--arm local_claude_1/third-troll/champion-orchard-v6-instrument.rs --out local_claude_1/third-troll/results/smoke-orchard.json` — PASS 24/24, a third troll in 21/24, median turn 119, funding median 103, 3 × "bill never paid by turn 200", stalled [], own-score sum +1193 (+1298 on the 21).
4. Read `readable/diffs/orchard.diff` (+313 / −32): one sentence — can anything in it plant on a door of our shack or on a shack, let an own troll chop an orchard tree while the third troll is wanted, plant before the second troll is trained, or let a troll CHOP while the bill is being collected — or "nothing".

**Return** one verdict message: REPRODUCED or NOT REPRODUCED, with the two hashes, the bed's counts, the smoke's numbers, and your one sentence. Dead means: the first differing line, and stop; no edits to the generators. If NOT REPRODUCED: remove `orchard-r2` from `local_claude_1/ladder-queue/queue.json` in the VM checkout `/home/tarstars/prj/troll_farm` and say so. Budget: one run of each, one message, today. No Arena.
