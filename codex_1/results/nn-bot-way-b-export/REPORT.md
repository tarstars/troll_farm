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
- Generated submission: `cgauto/submissions/candidate-nn-clone.rs`, 50,780 characters
  (137,972 UTF-8 bytes), SHA-256
  `915ed88ba9a7ce0109090a835bb95b78d19c66c48232802c864d80256ba63dcd`.
- Readable generated source: 155,589 bytes, SHA-256
  `4c84cbcad36148a1648185a9f955c4e9b524ba166596fbe49968ad1fbb2e0770`.

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
x86-64 AVX2/SSE intrinsics. Static-map routing is computed once and reused on every turn.

## Gate evidence

`bed-full-bot.json` records the final generated source hash above and all five gates as true:

- Python quantized checkpoint versus signed original clone: 48/48 games and 13,206/13,206
  turns identical, with zero differences.
- Compiled Rust bot versus the same signed replay stream: 48/48 games and 13,206/13,206 turns
  identical, with zero differences.
- Worst first turn: 13.407 ms (limit 500 ms).
- Warm turns: 6.492 ms median, 12.919 ms p99, 17.477 ms maximum (p99 limit 15 ms).
- Compacted source: 50,780 characters (limit 100,000).

`tests/test_export_full_actor.py` passes 5/5. It covers exact shipping/payload counts, effective
bit width and group size, every-byte Unicode packing round-trip, quantization layout, foreign
plan-vocabulary rejection, and the sanitizer/argmax manifest contract. The final submission also
compiles directly with stable `rustc --edition=2021 -O -Awarnings`.

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

The Python bench result is retained alongside all 48 replay streams. Its replay SHA-256 is
`03a1ef8ba5becef06c19020c96da50b94f813b1d9c8f18fa06815f8543b5c717`; the signed original replay
SHA-256 recorded by the bed is
`6eceb8caf5b07cf188bc8d085f28fc2a1c9fa87e891a33f7a70a4d81f031205c`.
