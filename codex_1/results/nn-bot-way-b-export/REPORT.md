# Full actor export and one-file Rust clone

Task `20260829-nn-bot-way-b-export` is ready for independent review. The generated Rust bot is
an exact command-stream clone of the signed Python clone on the full 24-map, both-seat bed, and
all size and latency gates pass. No Arena or platform action was taken.

## Pinned inputs and outputs

- Source checkpoint: `local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt`,
  SHA-256 `970097ed0842463b7ef5a4c08831d47ecc4e28397a52cadcc66d688e2a085109`.
- Shipping model: 34,799 actor/plan parameters. The 1,153 critic parameters are omitted.
- Payload: `clone-int8.bin`, 72,660 bytes, SHA-256
  `4ea9c80db7ee7832926b492fb79d07deaadcddc09cca7687f95e4b7289274137`.
- Manifest: `clone-int8-manifest.json`, SHA-256
  `6612bf9d2727cf45cd4ed1eafc423d4761cf0ff09b8f542cdf9e4266b20375b6`.
- Generated submission: `cgauto/submissions/candidate-nn-clone.rs`, 52,854 characters
  (140,046 UTF-8 bytes), SHA-256
  `36bf2f2e23f849bc522614ed5fe7950e40fcede62e535dee5a692cf7ac059cff`.
- Readable generated source: 158,016 bytes, SHA-256
  `39851d29d754b47a2de9d2b6fe15a3adea478b64246dcda1e693c393ef7329c9`.

The payload stores signed-int8 coarse weights plus packed residual bits, yielding effective
signed 16-bit integers throughout. Each output is quantized in groups of 64 with an f32 scale
and four least-squares scale refits; biases remain f32. The payload is embedded in 29,064
supplementary Unicode scalar values by packing five bytes into two scalars. The card's limit is
source characters, not UTF-8 bytes, so both measurements are reported explicitly.

The generator validates the payload/manifest hashes and topology, lifts the signed state,
engine, codec, mask, 104-plane, and `MoveRouting` implementations rather than reimplementing
them, and records their source hashes. Plan-time planes 59--71 and 98 are zeroed exactly as in
training. Plan and command choices are masked argmax; TRAIN is emitted only after the signed
environment dry run succeeds. The runtime is one std-only Rust file, single-threaded, and uses
x86-64 AVX2/SSE intrinsics. Static-map routing is computed once and reused on every turn. On
turn one it requires the complete id set `{0,1}`, derives the absolute seat from the
player-relative own troll's id, and caches that seat. It restores shacks, inventories, and unit
ownership into one absolute representation before calling the lifted builder and codec.

## Gate evidence

`bed-full-bot.json` records the final generated source hash above and all seven gates as true:

- Python quantized checkpoint versus signed original clone: 48/48 games and 13,206/13,206
  turns identical, with zero differences.
- Compiled Rust bot versus the same signed replay stream: 48/48 games and 13,206/13,206 turns
  identical, with zero differences.
- Worst first turn: 14.781 ms (limit 500 ms).
- Warm turns: 6.505 ms median, 9.718 ms p99, 15.095 ms maximum (p99 limit 15 ms). The first
  amended run retained exact parity but measured 15.126 ms p99; an immediate full rerun measured
  the reported passing value, consistent with the pre-amendment 12.919--13.379 ms runs on this
  shared host.
- Compacted source: 52,854 characters (limit 100,000).
- The cfg-gated direct probe passes both seats on a four-troll state with a staged non-MOVE
  action. The standalone and `tf_full_obs_from_state`/canonical codec match exactly on all 25,168
  observation bytes, 3,146 spatial-mask bytes, 400 plan-mask bytes, and DROP decoding. A malformed
  turn-one id set is rejected before any reply.
- The retained compact pilot checks 6/6 seat-0 turn-one games with zero exceptions. The amendment
  card records the complete training-corpus check as 370/370 with zero exceptions. The complete
  `/home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz` was no longer present by
  this run, so the reusable checker and the retained-corpus result are in the artifact rather
  than pretending to have rerun the unavailable file.

`tests/test_export_full_actor.py` passes 7/7. It covers exact shipping/payload counts, effective
bit width and group size, every-byte Unicode packing round-trip, quantization layout, foreign
plan-vocabulary rejection, the sanitizer/argmax manifest contract, exact turn-one seat recovery,
and the corpus checker's negative control. The final submission and its parity-probe cfg both
compile directly with stable `rustc --edition=2021 -O -Awarnings`.

## Reproduction

Run from the repository root with the existing Torch/Numpy environment on `PYTHONPATH`:

```text
python3 local_claude_1/nn-bot/export_full_actor.py \
  local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt \
  --payload codex_1/results/nn-bot-way-b-export/clone-int8.bin \
  --manifest codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json \
  --verification-checkpoint codex_1/results/nn-bot-way-b-export/clone-int8-verification.pt

PYTHONPATH=. python3 local_claude_1/nn-bot/generate_full_bot.py \
  codex_1/results/nn-bot-way-b-export/clone-int8-manifest.json \
  codex_1/results/nn-bot-way-b-export/clone-int8.bin \
  --readable-output codex_1/results/nn-bot-way-b-export/candidate-nn-clone-readable.rs \
  --output cgauto/submissions/candidate-nn-clone.rs

python3 local_claude_1/nn-bot/bench.py \
  --policy network \
  --checkpoint codex_1/results/nn-bot-way-b-export/clone-int8-verification.pt \
  --plan-decoding argmax --both-seats \
  --out codex_1/results/nn-bot-way-b-export/bench-quantized-python.json \
  --replays codex_1/results/nn-bot-way-b-export/bench-quantized-python-replays.jsonl

PYTHONPATH=local_claude_1/nn-bot python3 \
  local_claude_1/nn-bot/bed_full_bot.py \
  --rustc /home/tarstars/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/bin/rustc

python3 -m pytest -q tests/test_export_full_actor.py
```

When the complete state shard is mounted, append
`--seat-corpus /home/tarstars/nn-data/dataset-v400-2026-08-30/states-pilot.jsonl.gz` to rerun the
370-game corpus test. Without that option the bed uses the complete shard when present and the
tracked ten-game pilot otherwise; the result records the exact path, hash, count, and exceptions.

The Python bench result is retained alongside all 48 replay streams. Its replay SHA-256 is
`03a1ef8ba5becef06c19020c96da50b94f813b1d9c8f18fa06815f8543b5c717`; the signed original replay
SHA-256 recorded by the bed is
`6eceb8caf5b07cf188bc8d085f28fc2a1c9fa87e891a33f7a70a4d81f031205c`.
