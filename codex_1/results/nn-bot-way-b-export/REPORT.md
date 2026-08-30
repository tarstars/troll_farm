# Full actor export and portable one-file Rust clone

Task `20260829-nn-bot-way-b-export` is ready for independent review after amendments (d),
(e), and (f). The generated Rust bot is command-identical to the signed Python clone on the
full 24-map, both-seat bed through both its runtime-selected AVX2 path and its forced baseline
fallback. All functional, fallback-latency, and UTF-16 size gates pass. The three timing samples
in this report are from the VM and are explicitly informational; the coordinator owns the
quiet host-of-record timing certificate. No Arena or platform action was taken.

## Pinned inputs and outputs

- Source checkpoint: `local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt`,
  SHA-256 `970097ed0842463b7ef5a4c08831d47ecc4e28397a52cadcc66d688e2a085109`.
- Shipping model: 34,799 actor/plan parameters. The 1,153 critic parameters are omitted.
- Payload: `clone-int8.bin`, 72,660 bytes, SHA-256
  `4ea9c80db7ee7832926b492fb79d07deaadcddc09cca7687f95e4b7289274137`.
- Manifest: `clone-int8-manifest.json`, SHA-256
  `6612bf9d2727cf45cd4ed1eafc423d4761cf0ff09b8f542cdf9e4266b20375b6`.
- Generated submission: `cgauto/submissions/candidate-nn-clone.rs`, SHA-256
  `4c5a096d627932edbb796e1af350e1a4518b702f959a05ed40cae515f0a53b06`.
  It is 54,218 Unicode code points, 83,282 UTF-16 code units, and 141,410 UTF-8 bytes.
- Readable generated source: 159,814 UTF-8 bytes, SHA-256
  `0139149db5110f6d4ff7ed6c8e7337c543eec0ee349fb9b91d42f17c5c420111`.

The platform gate is now the UTF-16 count: 83,282 is below 100,000 with 16,718 units of
headroom. The old Python-`len` count remains visible as the code-point count but is no longer
the gate.

## Runtime dispatch and numerical contract

The normal file detects AVX2 once in `Actor::new` with
`std::arch::is_x86_feature_detected!("avx2")`. AVX2 selects the existing 8-lane kernel. A
worker without AVX2 selects a baseline x86-64 fallback that uses SSE2 4-lane operations plus
the scalar tail; the fallback has no `target_feature` annotation and contains no AVX
intrinsics. Both paths visit weights in the same order and use separate multiply and add
operations, without enabling fused multiply-add.

The bed compiles the same source a second time with `--cfg tf_nn_force_fallback`. Separate
path probes report `avx2` for the normal VM build and `baseline_fallback` for that forced build.
This makes the fallback path a directly executed gate, not an inspection-only claim.

The generator still validates the payload/manifest hashes and topology, lifts the signed
state, engine, codec, mask, 104-plane, and `MoveRouting` implementations rather than
reimplementing them, and records their source hashes. Plan-time planes 59--71 and 98 are zeroed
exactly as in training. Plan and command choices are masked argmax; TRAIN is emitted only after
the signed environment dry run succeeds. On turn one the runtime requires the complete id set
`{0,1}`, derives the absolute seat from the player-relative own troll's id, and caches it.

## Gate evidence

`bed-full-bot.json` records all ten functional gates as true:

- Python quantized checkpoint versus signed original clone: 48/48 games and
  13,206/13,206 commands identical, with zero differences.
- Runtime-dispatched compiled Rust (path probe: AVX2): 48/48 games and
  13,206/13,206 commands identical, with zero differences.
- Forced baseline fallback: 48/48 games and 13,206/13,206 commands identical, with zero
  differences. First-turn max was 14.277 ms; warm median 8.776 ms; warm p99 12.529 ms; warm
  max 20.360 ms. The fallback is below the 50 ms platform limit.
- The cfg-gated direct probe passes both seats on a four-troll state with a staged non-MOVE
  action. Observation, spatial mask, plan mask, decoded command, and seat all match the signed
  shared runtime. A malformed turn-one id set is rejected before any reply.
- The compact tracked pilot checks 6/6 seat-0 turn-one games with zero exceptions. The full
  370-game rule already passed twice: once for the coordinator and once independently for
  `claude_1`. This run did not read the restored external shard because the mandatory storage
  preflight failed: neither archive backend is mounted. The JSON cites the accepted 370-game
  result rather than claiming a third execution.
- Source size is 83,282 UTF-16 units, below the 100,000-unit gate.

Focused tests pass 10/10. They cover exact shipping/payload counts, effective bit width and
group size, every-byte Unicode packing round-trip, all three size units, quantization layout,
foreign plan-vocabulary rejection, the sanitizer/argmax manifest contract, exact turn-one seat
recovery, the corpus checker's negative control, the frozen timing calculation, structural
separation of the AVX2 and fallback kernels, and an actual stable-Rust forced-fallback path
probe. The final submission, forced-fallback build, parity-probe build, and path-probe builds
all compile directly with stable `rustc --edition=2021 -O -Awarnings`.

## Timing rule and this VM's information-only result

The functional bed ran once per path. The normal timing sample ran three complete times. The
VM's warm p99 values were **15.731, 13.363, and 15.026 ms**; the median was **15.026 ms** and
all were below 20 ms. First-turn maxima were 28.313, 31.516, and 28.387 ms.

This is not the host-of-record certificate: `timing_certification.context` is `information` and
`certified` is null. Numerically the VM misses the 15 ms median line by 0.026 ms. Per the
coordinator's frozen rule, that does not fail the artifact. Certification is exactly three runs
on the quiet `/home/tarstars` host, pass if median warm p99 is at most 15 ms and every run is at
most 20 ms. Running with `--timing-context host-of-record-quiet` applies that gate.

## Reproduction

Run from the repository root with the existing Torch/Numpy environment on `PYTHONPATH`:

```text
PYTHONPATH=. python3 local_claude_1/nn-bot/generate_full_bot.py \
  codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json \
  codex_1/results/nn-bot-way-b-export/clone-int8.bin \
  --readable-output codex_1/results/nn-bot-way-b-export/candidate-nn-clone-readable.rs \
  --output cgauto/submissions/candidate-nn-clone.rs

PYTHONPATH=local_claude_1/nn-bot python3 \
  local_claude_1/nn-bot/bed_full_bot.py \
  --rustc /home/tarstars/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc \
  --seat-corpus local_claude_1/nn-bot/results/pilot/states-pilot.jsonl.gz \
  --timing-context information

/home/tarstars/venvs/nn-bot/bin/python -m pytest -q tests/test_export_full_actor.py
```

For the coordinator's quiet host run, use `--timing-context host-of-record-quiet`. If the
external archive preflight passes, the retained corpus argument may be replaced with
`/home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz` to repeat the accepted
370-game seat check.

## VM dataset-removal question

I did not remove `/home/tarstars/nn-data/`. It was already absent when my corrected 14:57Z
artifact ran, and my published report said so at that time. The available repository and message
record does not identify who removed it or when. This session deleted nothing; the coordinator's
restored copy remains untouched because the external-storage read preflight failed.
