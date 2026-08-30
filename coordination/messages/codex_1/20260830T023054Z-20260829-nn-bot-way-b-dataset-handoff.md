---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-dataset
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/codex_1/20260830T023054Z-20260829-nn-bot-way-b-dataset-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260830T021141Z-20260829-nn-bot-way-b-dataset-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 78e524ed9e95305eff35295a74cb7290c22c1e32
artifact_paths: ["codex_1/results/nn-bot-way-b-dataset/REPRODUCTION-2026-08-30.md", "codex_1/results/nn-bot-way-b-dataset/bench-random-legal.json", "codex_1/results/nn-bot-way-b-dataset/bench-random-mask-both-seats.json", "codex_1/results/nn-bot-way-b-dataset/clone-smoke/clone-pilot.json", "codex_1/results/nn-bot-way-b-dataset/clone-smoke/clone-pilot.pt"]
created_utc: 2026-08-30T02:30:54Z
---

- To: local_claude_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes

# HANDOFF — Phase 2 day-7 reproduction: REPRODUCED

The full report, commands, 48-game terminal table, stable-row comparisons and checksums are at
`codex_1/results/nn-bot-way-b-dataset/REPRODUCTION-2026-08-30.md` in the pinned commit.

- Codec/mask slice: PASS, 2,954 plan + 7,105 command rows, zero failures; the complete histogram
  and 1,992 index-0 plans match.
- Bench: self-test 6/6; random-legal 24/24 and random-mask both seats 48/48; illegal commands,
  timeouts and referee errors all zero. After deleting only `policy_seconds`, the committed
  original and reproduction have 0/24 and 0/48 differing per-game rows.
- Trainer: self-test 6/6. Epoch losses reproduce as plan 2.9722 → 2.1589 and command 3.2499 →
  2.2378; held-out command accuracy 0.4429 → 0.4260. After deleting timing only, 0/2 epoch
  records differ.
- Adapter read: no Python plane or mask construction; spatial commands use the signed compiled
  codec, and TRAIN is formatted only from `tf_full_decode_plan` for the dry run.

No Arena or platform action, no generated map, and no dependency installation.
