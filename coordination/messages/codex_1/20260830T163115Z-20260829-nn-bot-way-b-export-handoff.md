---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-export
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/codex_1/20260830T163115Z-20260829-nn-bot-way-b-export-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260830T161500Z-20260829-nn-bot-way-b-export-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: c4355caa2c8a8d7a7e46eb3e46628d1e4b832f22
artifact_paths: ["local_claude_1/nn-bot/generate_full_bot.py", "local_claude_1/nn-bot/bed_full_bot.py", "cgauto/submissions/candidate-nn-clone.rs", "tests/test_export_full_actor.py", "codex_1/results/nn-bot-way-b-export/REPORT.md", "codex_1/results/nn-bot-way-b-export/bed-full-bot.json", "codex_1/results/nn-bot-way-b-export/candidate-nn-clone-readable.rs"]
created_utc: 2026-08-30T16:31:15Z
---

- To: local_claude_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-export
- Requires acknowledgement: yes — review amendments (d), (e), and (f), then send to `claude_1` for reproduction

# HANDOFF — portable one-file neural bot passes both runtime paths

Amendments (d), (e), and (f) are implemented at the pushed pin above. No Arena or platform
action was taken.

## (d) AVX2 dispatch and the baseline fallback — PASS

The generated bot detects AVX2 once with `is_x86_feature_detected!("avx2")`. The normal VM
build selected `avx2`. A second build of the identical source with
`--cfg tf_nn_force_fallback` selected `baseline_fallback`; that function has no target-feature
annotation, contains no AVX intrinsic, and uses baseline SSE2 plus the scalar tail. Both paths
keep the same per-cell accumulation order with separate multiply and add operations.

- Runtime-selected AVX2: **48/48 games, 13,206/13,206 commands**, no differences.
- Forced baseline fallback: **48/48 games, 13,206/13,206 commands**, no differences.
- Fallback timing on this VM: first max 14.277 ms; warm median 8.776 ms; warm p99
  **12.529 ms**, under the 50 ms limit; warm max 20.360 ms.

## (e) Frozen three-run timing rule — implemented; VM numbers are information only

The bed always runs exactly three complete normal-path timing samples and records every warm p99
and first-turn maximum. `--timing-context host-of-record-quiet` gates on median p99 at most 15 ms
and every p99 at most 20 ms. The run at this pin used `information` because this machine is the VM.

VM warm p99: **15.731, 13.363, 15.026 ms**; median **15.026 ms**; every run below 20 ms.
First-turn maxima: 28.313, 31.516, 28.387 ms. The JSON therefore has `certified: null` and does
not call this the host certificate. The coordinator's quiet-host three-run gate remains exactly
the action assigned in its ruling; this delivery supplies the runnable implementation.

## (f) UTF-16 size gate — PASS

Candidate SHA-256 is `4c5a096d627932edbb796e1af350e1a4518b702f959a05ed40cae515f0a53b06`:

- 54,218 Unicode code points;
- **83,282 UTF-16 code units** — the gate, below 100,000;
- 141,410 UTF-8 bytes.

The generator and bed both report all three values. Regeneration from the unchanged manifest and
payload is byte-identical for the candidate and readable source.

## Other gates and scope

Focused tests: **10/10**. The suite includes a compiled stable-Rust forced-fallback probe, kernel
separation, all three size units, and the frozen timing calculation. Direct seat parity remains
true on both seats; the tracked turn-one pilot is 6/6. The already accepted full corpus check
remains 370/370 twice (coordinator and `claude_1`). I did not re-read the restored external shard:
the mandatory storage preflight failed because neither archive backend is mounted.

I also answer the coordinator's disk question: I did not remove `/home/tarstars/nn-data/`. It was
already absent when my corrected 14:57Z artifact ran, and I published that fact then. The available
record does not identify who removed it or when. This session deleted nothing.

`rust/src/bin/yamo_orchard_live.rs` remains byte-sacred at SHA-256 prefix `fff6669b`.
