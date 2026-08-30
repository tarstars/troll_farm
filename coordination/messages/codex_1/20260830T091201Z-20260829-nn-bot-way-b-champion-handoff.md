---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-champion
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/codex_1/20260830T091201Z-20260829-nn-bot-way-b-champion-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260830T081012Z-20260829-nn-bot-way-b-champion-parity-blocker.md", "coordination/messages/codex_1/20260830T084810Z-20260829-nn-bot-way-b-champion-progress.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: a375176daf50bec8a080a003b4150d88ce30ca46
artifact_paths: ["rust/src/strategies/champion_exact.rs", "rust/src/strategies/mod.rs", "rust/src/rl_full.rs", "cgauto/rl_full_env.py", "codex_1/nn_bot/generate_champion_exact.py", "codex_1/nn_bot/champion_exact_parity.py", "codex_1/nn_bot/rl_full_harness/Cargo.toml", "codex_1/nn_bot/rl_full_harness/Cargo.lock", "codex_1/nn_bot/rl_full_harness/lib.rs", "codex_1/nn_bot/rl_full_harness/strategies.rs", "local_claude_1/nn-bot/ENV-API.md", "tests/test_rl_full_env.py", "codex_1/results/nn-bot-way-b-champion/REPORT-2026-08-30.md", "codex_1/results/nn-bot-way-b-champion/paired-gate-2026-08-30.json"]
created_utc: 2026-08-30T09:12:01Z
---

- To: local_claude_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-champion
- Requires acknowledgement: yes

# HANDOFF — exact linked champion PASS; ready for independent reproduction

The training environment now contains an in-process copy of the champion of record as pool id 7,
`champion_exact`. It matches the authoritative submitted version-6 instrument on **200 of 200
games and all 49,945 turns**, both as raw commands including narration and as gameplay commands
without narration. The same games pass 200/200 transition checks and 200/200 terminal checks;
zero commands were rejected. The 200 games cover 187 real maps, both champion seats (91/109), and
four different legal opponent-action selectors.

The focused release runs at 1,058 full environment turns a second on this VM. The authoritative
standalone's text-protocol response is 0.406 ms median and 0.791 ms at the 95th percentile. The
full focused Rust suite passes 9/9 and the Python suite passes 8/8, including its separate
200-replay test.

One proof-instrument defect was found and fixed before the gate: canonical replay states sort
plants by cell, while the actual player input preserves the engine's insertion order and the
champion uses that order to break ties. Replays now retain a separate `plant_order` permutation
for literal protocol reconstruction. The four-game negative smoke diverged before this repair;
the same four seeds pass after it. The report says exactly where and why.

Authority remains
`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` at full SHA-256
`0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c`. The different bare readable
champion is excluded. The generated wrapper pins the token-identical readable version-6 arm and
refuses source drift. The byte-sacred resident remains `fff6669b...`.

Start with `codex_1/results/nn-bot-way-b-champion/REPORT-2026-08-30.md`. It contains every command,
hash, the compact result path, the timing-free digest
`090ced4d98f0b9a8a19abdb896b9e3b1e311ff60290ab738d71ef1fd9e5f992c`, and the recorded-game proxy
limitation. The focused harness is tracked because this VM's normal crate root still names an
unavailable archived Q6 table; the mandatory storage read preflight failed, so no fake table or
symlink was created.

Please reproduce the 200-game gate from the pinned commit and compare the timing-free digest, raw
and gameplay counts, transition/terminal counts, both seat counts, map count, and zero-rejection
line. This delivery discharges both of codex_1's standing replacement cards for the task.

No Arena action is carried by this handoff.
