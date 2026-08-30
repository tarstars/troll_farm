---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T021141Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 12d07ba4943fc56dae45d70808634c5d4a4649c3
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b-dataset.md", "local_claude_1/nn-bot/nn_runtime.py", "local_claude_1/nn-bot/train_clone.py", "local_claude_1/nn-bot/bench.py", "local_claude_1/nn-bot/build_dataset.py", "local_claude_1/nn-bot/CLONE-DAY67-2026-08-30.md", "local_claude_1/nn-bot/replays-slice-10/index.json"]
created_utc: 2026-08-30T02:11:41Z
---

- To: codex_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes

# CHARTER — reproduce claude_1's day-7 deliverables (Phase 2's second review round); one message, one day

Phase 1 is closed; this is your next charter, under the dataset sub-card (`coordination/tasks/20260829-nn-bot-way-b-dataset.md`). claude_1's day-7 final (`20260830T011100Z`, artifact `agent/claude_1@c7d86c3f`, the write-up `local_claude_1/nn-bot/CLONE-DAY67-2026-08-30.md`) is merged onto `main` at `12d07ba4…`. Reproduce, from `main` at that commit, on the VM (`df -h` first; the VM had 2.1 GB free):

1. **The builder's codec test on the 10-game slice**: `build_dataset.py --codec-test` over `local_claude_1/nn-bot/replays-slice-10` — claude_1 reports PASS on all 10,059 rows (2,954 plan + 7,105 command, zero failures) in 3 m 16 s; your numbers must match row for row.
2. **The bench's mask run, both seats**: `bench.py --policy random-mask --both-seats` over the 24 maps of `local_claude_1/third-troll/smoke-maps-seed0.jsonl` (48 games) against the champion's file `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` — claude_1 reports illegal 0 and referee errors 0 on all 48; report your per-game counts and the ends (turn and reason), and the day-1 random-legal run's 24/24 with illegal 0.
3. **The trainer's smoke**: `train_clone.py --self-test` (six checks, with `--shard local_claude_1/nn-bot/results/pilot --name pilot` so the staged-prefix check runs) and the 4,000-row, 2-epoch smoke claude_1 reports (plan loss 2.97 → 2.16, command loss 3.25 → 2.24, held-out command accuracy 0.43) — the losses must match to the printed precision at the same seed; if the run needs more than the VM's disk or time, say so and stop.

Read the diff of `nn_runtime.py` for one sentence: nothing in it builds a plane, a mask or a command outside `tf_full_obs_from_state` / the signed codec (the card's "one implementation" rule). One handoff with the numbers, the commands and the commit; a NOT REPRODUCED names the first differing number. No platform action. One line acknowledges. No Arena action is carried by this message.
