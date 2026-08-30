---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-export
from: local_claude_1
to: ["claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T153500Z-20260829-nn-bot-way-b-export-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260830T145709Z-20260829-nn-bot-way-b-export-correction.md"]
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: b6075fe8f76dbe7ed453472e6bccd1bac55046be
artifact_paths: ["local_claude_1/nn-bot/export_full_actor.py", "local_claude_1/nn-bot/generate_full_bot.py", "local_claude_1/nn-bot/bed_full_bot.py", "cgauto/submissions/candidate-nn-clone.rs", "tests/test_export_full_actor.py", "codex_1/results/nn-bot-way-b-export/REPORT.md", "codex_1/results/nn-bot-way-b-export/bed-full-bot.json"]
created_utc: 2026-08-30T15:35:00Z
---

- To: claude_1
- CC: codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-export
- Requires acknowledgement: yes

# HANDOFF — reproduce codex_1's one-file clone bot (Phase 4 engineering)

codex_1 delivered the amended export at `agent/codex_1@5be68352dc923458694beb913da2d2d73e206507`, merged onto `main` as `b6075fe8f76dbe7ed453472e6bccd1bac55046be` (the pin above)
(its correction of 14:57Z; the report is `codex_1/results/nn-bot-way-b-export/REPORT.md`). The
coordinator's own check on the host: the candidate `cgauto/submissions/candidate-nn-clone.rs` is
52,854 characters with SHA-256 `36bf2f2e23f849bc…`; the focused suite is 7/7; regeneration from the
manifest and payload is byte-identical (the same hash); the 48-game bed with the full corpus check
is running on the host now. Your reproduction is the second, independent one.

## What to reproduce, on the VM, from that pushed commit

1. `tests/test_export_full_actor.py` — the 7 tests.
2. Regeneration: `generate_full_bot.py` from `clone-int8-manifest.json` + `clone-int8.bin` gives a
   file with the candidate's exact SHA-256 and character count.
3. The bed: `bed_full_bot.py --rustc <stable rustc>` — the Python quantized checkpoint against the
   signed original clone stream 48/48 games and 13,206/13,206 turns; the compiled Rust bot the same;
   both difference lists empty; the direct parity probe on both seats (observation, both masks,
   DROP decoding); the timing gates (first turn ≤ 500 ms, warm p99 ≤ 15 ms — report your numbers,
   the VM is slower than the host, so if p99 fails there say so with the number and do not call it
   a failure of the artifact; the host's number is the one of record).
4. The corpus check `--seat-corpus /home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz`
   (370 seat-0 turn-one games, zero exceptions). That directory is no longer on the VM (see below); the
   coordinator restores it from the host copy (checksums in `SHA256SUMS`) before you start — verify
   the checksum first.

Report: PASS/FAIL per item with the numbers and hashes, in one ack-required handoff on this task,
pinned to the commit you ran. A mismatch of any hash or any non-empty difference list is a FAIL —
report it as such with the diff, do not fix codex_1's code on this task.

## The VM's disk

The VM is at 96 % (832 MB free) and `/home/tarstars/nn-data/` is gone from it. Do not delete
anything to make room — report what fills the disk (`du -xsh /home/tarstars/*`) in your handoff;
the coordinator brings the question to the owner. If a build fails for lack of space, say so and stop.

No platform action is part of this task.
