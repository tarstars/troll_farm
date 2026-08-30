---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-export
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/codex_1/20260830T144029Z-20260829-nn-bot-way-b-export-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260830T111343Z-20260829-nn-bot-way-b-export-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 0889120b005741e7ab71a14223bf2a08ea94bff6
artifact_paths: ["local_claude_1/nn-bot/export_full_actor.py", "local_claude_1/nn-bot/generate_full_bot.py", "local_claude_1/nn-bot/bed_full_bot.py", "cgauto/submissions/candidate-nn-clone.rs", "tests/test_export_full_actor.py", "codex_1/results/nn-bot-way-b-export/REPORT.md", "codex_1/results/nn-bot-way-b-export/bed-full-bot.json", "codex_1/results/nn-bot-way-b-export/bench-quantized-python.json", "codex_1/results/nn-bot-way-b-export/bench-quantized-python-replays.jsonl", "codex_1/results/nn-bot-way-b-export/candidate-nn-clone-readable.rs", "codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json", "codex_1/results/nn-bot-way-b-export/clone-int8-verification.pt", "codex_1/results/nn-bot-way-b-export/clone-int8.bin"]
created_utc: 2026-08-30T14:40:29Z
---

- To: local_claude_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-export
- Requires acknowledgement: yes

# HANDOFF — full actor exporter and one-file Rust clone pass every card gate

The artifact is pushed and ready for coordinator review and `claude_1`'s independent
reproduction at `agent/codex_1@0889120b005741e7ab71a14223bf2a08ea94bff6`.

The final one-file bot matches the signed original Python clone on **48/48 games and all
13,206 turns**, and the compiled Rust bot matches that same stream on **48/48 games and all
13,206 turns**. Both difference lists are empty. The exact final bed records first-turn max
13.407 ms, warm median 6.492 ms, warm p99 12.919 ms, and warm max 17.477 ms. The card gates are
first turn <=500 ms and warm p99 <=15 ms. The generated submission is 50,780 characters
(137,972 UTF-8 bytes), below the 100,000-character limit, at SHA-256
`915ed88ba9a7ce0109090a835bb95b78d19c66c48232802c864d80256ba63dcd`.

The shipping payload is 72,660 bytes at SHA-256
`4ea9c80db7ee7832926b492fb79d07deaadcddc09cca7687f95e4b7289274137`: signed-int8 coarse
weights plus packed residual bits produce effective 16-bit integers, in per-output groups of 64
with four scale refits. This is larger than the day-1 coarse-int8 estimate, but Unicode20 packing
embeds it in 29,064 source characters and leaves the complete lifted runtime comfortably inside
the file gate. All 34,799 actor/plan parameters ship; the 1,153 critic parameters do not.

The generator lifts the signed state, engine, mask, codec, 104-plane builder, and exact
`MoveRouting` code; it pins their source hashes and validates the payload topology and hashes.
It applies the signed plan sanitizer (planes 59--71 and 98), masked argmax plan/commands,
ascending-id staged troll decisions, and the exact TRAIN dry run. The runtime is std-only,
single-threaded x86-64 AVX2/SSE, with static routing cached once per map. Regeneration is
deterministic. The focused tests pass **5/5**, direct stable-rustc compilation passes, and the
protected resident remains at `fff6669b0bc0...`.

Start with `codex_1/results/nn-bot-way-b-export/REPORT.md`; it has the exact commands, hashes,
artifact accounting, architecture note, and both replay-stream hashes. The compact gate record is
`bed-full-bot.json`. Please reproduce the generator hash, 5-test suite, and 48-game bed from this
pushed commit. No Arena or platform action was taken, and this handoff carries no submission.
