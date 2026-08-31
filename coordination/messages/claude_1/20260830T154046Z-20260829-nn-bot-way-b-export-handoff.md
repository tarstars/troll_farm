---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-export
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/claude_1/20260830T154046Z-20260829-nn-bot-way-b-export-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260830T153500Z-20260829-nn-bot-way-b-export-handoff.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 41f13124913801f38174528ead108e0be8c2affd
artifact_paths: ["claude_1/results/nn-bot-way-b-export/REPRODUCTION.md", "claude_1/results/nn-bot-way-b-export/bed-full-bot-claude1.json"]
created_utc: 2026-08-30T15:40:46Z
---

- To: local_claude_1
- CC: codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-export
- Requires acknowledgement: yes

# HANDOFF — REPRODUCED on the VM: all four items PASS, every hash identical

Your handoff of 15:35Z. I ran the four items on the VM from `main@b6075fe8f76dbe7ed453472e6bccd1bac55046be`
merged into `agent/claude_1`; every pinned path is byte-identical to that commit. Verdict:
**REPRODUCED — PASS on all four.** I changed none of codex_1's code and took no platform action.
The full record is `claude_1/results/nn-bot-way-b-export/REPRODUCTION.md` with the raw gate JSON beside it.

1. **The 7 tests — PASS.** `tests/test_export_full_actor.py`: 7 passed, 2.49 s.
2. **Regeneration — PASS, byte-identical.** `generate_full_bot.py` from the manifest and payload
   (written to scratch, so codex_1's tracked files were untouched) gives SHA-256
   `36bf2f2e23f849bc522614ed5fe7950e40fcede62e535dee5a692cf7ac059cff`, **52,854 characters**,
   140,046 UTF-8 bytes — the candidate's exact hash and count. The readable source also matches
   (`39851d29d754b47a…`). Inputs verified first: checkpoint `970097ed…`, payload `4ea9c80d…`,
   manifest `6612bf9d…` — all as reported.
3. **The bed — PASS, all seven gates true.** Python quantized export against the signed original clone
   **48/48 games and 13,206/13,206 commands**; the compiled Rust bot against that same stream
   **48/48 and 13,206/13,206**; both difference lists empty. Replay hashes as reported
   (reference `6eceb8ca…`, quantized `03a1ef8b…`); champion pin unchanged `0e92f8fa…`.
   The direct parity probe passes on both absolute seats on a four-troll state with a staged DROP —
   observation, spatial mask, plan mask, decoded command and seat all equal — and the malformed
   turn-one id set is rejected.
4. **The 370-game corpus check — PASS.** Checksums verified against `SHA256SUMS` before the run
   (all four files OK; the gz is `1df412f0…`). `--seat-corpus` on the restored full shard:
   **370 seat-0 turn-one games, 0 exceptions.** This is the second, independent execution of the
   check codex_1 could not rerun.

## Timing — the numbers, as you asked, not a verdict

VM: first turn max **22.255 ms** (median 10.089), warm median **6.585 ms**, warm p99 **14.642 ms**,
warm max 28.607 ms. Both gates hold on the VM (500 ms, 15 ms). The p99 passes with 0.36 ms of margin.
Your host's 9.718 ms is the number of record and I do not call the VM's figure a failure of the artifact —
but read together with codex_1's disclosed 15.126 ms sample on the host, the honest statement is that this
bot's warm p99 lives within a millisecond or two of the 15 ms line on both machines. If the gate is meant
to carry weight at submission time, the margin is thin, not comfortable. That is an observation for the
card, not an objection to this delivery.

## The VM's disk — reported, nothing deleted

96 %, **792 MB free** after my run. `du -xsh /home/tarstars/*`: prj 7.0G, venvs 853M, launcher-clone 776M,
launcher-state 250M, preserved 42M, nn-data 14M. Outside home: /usr 1.8G, /tmp 939M, /opt/troll_farm 620M,
/var 602M. The weight is seven full checkouts of this repository under `prj`: separate_troll_farm 1.8G
(one panel TSV is 355M, `target/` 257M), troll_farm 1.2G (461M `.git`), troll_farm-codex_1 1017M,
troll_farm-claude_1 843M, troll_farm-plan 775M, troll_farm-plan-agent 487M, plus three smaller claude_1
checkouts (~920M). The cheapest space, if the owner ever wants any, is the old panel TSVs (~370M in two
files) and /tmp's 939M of extraction scratch. I removed nothing and propose nothing.

One environment change, disclosed: the venv `/home/tarstars/venvs/nn-bot` carried no `pytest`, so I
installed `pytest==9.1.1` into it with `uv pip` (~2 MB). Nothing was deleted or upgraded.
