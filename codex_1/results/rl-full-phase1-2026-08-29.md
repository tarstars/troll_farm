# Full-game neural environment Phase 1 — implementation and gates

Artifact source commit: `f94be850ad5ae32e16845cda19b434a5f6d4aa08` on
`agent/codex_1`. No Arena action was taken. The byte-sacred resident remained
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Delivered surface

- `rust/src/rl_full.rs`: real-map episode construction, 104-plane observations, plan and
  spatial masks, staged multi-troll commands, exact engine turns and end condition, seven opponent
  modes, replay/state hashes, Rayon batches, and the signed `tf_full_*` ABI.
- `cgauto/rl_full_env.py`: NumPy/ctypes vector wrapper, learner mini-step reward credit,
  Python-frozen opponent driver, legal random sampler, replay extraction, and an independent
  `sim/engine.py` replay verifier.
- `tests/test_rl_full_env.py`: ABI/shape/phase checks, batch-atomic invalid actions,
  deterministic batches, Python-opponent credit, 10,000 random masked learner actions,
  and 200 independently replayed self-play games.

The repository-native release library was built with:

```text
/home/tarstars/.cargo/bin/cargo build --manifest-path rust/Cargo.toml --release --lib
```

It completed in 58.19 s. `rust/target/release/libtroll_farm.so` was 3,461,280 bytes with
SHA-256 `53fbb32e62a84fa67e09b7b1b98e1e4dfee26e2b6ab74619278ae0b6b565fb2a`.

## Tests

The canonical Python suite ran against that native library:

```text
TF_FULL_TEST_LIBRARY=/home/tarstars/prj/troll_farm-codex_1/rust/target/release/libtroll_farm.so \
  /home/tarstars/.local/bin/uv run --with numpy pytest -q tests/test_rl_full_env.py
```

Result: **6 passed in 161.58 s**. This includes 10,000 accepted random masked learner actions and
**200/200** no-train self-play replays matching the independent Python simulator on every turn and
terminal hash.

A focused release harness importing the exact production `state.rs`, `engine.rs`, strategy sources,
byte-sacred resident source, and `rl_full.rs` ran 51 Rust tests:

```text
/home/tarstars/.cargo/bin/cargo test --release \
  --manifest-path /tmp/troll-full-check.iGsiu8/Cargo.toml --lib
```

Result: **51 passed in 21.88 s**. This includes all seven opponent modes completing legal real-map
games and cached routing matching `engine::next_cell` for every source, target, and speed 1–3 on
four maps. The focused harness was used because this worktree's unrelated `rl_q6_proposal` test
module has a historical compile-time TSV under unavailable bulk storage; the native non-test
library itself builds successfully, and no replacement dataset or symlink was created.

## Required 1,000-game gate

The gate ran the native library with fully random legal actions on both seats, real maps, exact
replay verification, 20 vector slots, and four Rayon threads:

```text
PYTHONPATH=. RAYON_NUM_THREADS=4 /home/tarstars/.local/bin/uv run --with numpy \
  python cgauto/rl_full_env.py --episodes 1000 --num-envs 20 --seed-base 200000 \
  --self-play --verify-replays --library rust/target/release/libtroll_farm.so \
  --output /tmp/rl-full-gate-native-f94be850.json
```

| measure | result |
|---|---:|
| target episodes | 1,000 |
| exact seed interval | 200000–200999, 1,000 unique |
| replay parity | **1,000/1,000** |
| illegal commands | **0** |
| terminal turns | 300 min / 300 max |
| wins | 424 |
| unique action hashes | 1,000 |
| unique terminal state hashes | 1,000 |
| learner mini-steps emitted | 921,562 |
| full turn-steps executed, including batch overshoot | 302,542 |
| elapsed | 2,232.234035836067 s |
| full turn-steps/s including Python replay verification | 135.5332797291952 |

The compact 227 KiB raw result has SHA-256
`111d3dc57156cb2d7d2176624a5dc2504db993be20a1915511a72240505cb969`. A second gate through the
focused cdylib produced identical episode details and identical non-timing counts, independently
confirming the native/focused link surfaces select the same actions and states.

## Speed lines

These lines omit replay verification and use the native library. The host has four logical CPUs,
so the 20-thread line is deliberately oversubscribed as requested.

```text
PYTHONPATH=. RAYON_NUM_THREADS=20 /home/tarstars/.local/bin/uv run --with numpy \
  python cgauto/rl_full_env.py --episodes 20 --num-envs 20 --seed-base 300000 \
  --self-play --library rust/target/release/libtroll_farm.so \
  --output /tmp/rl-full-speed-native-20-f94be850.json

PYTHONPATH=. RAYON_NUM_THREADS=4 /home/tarstars/.local/bin/uv run --with numpy \
  python cgauto/rl_full_env.py --episodes 4 --num-envs 4 --seed-base 301000 \
  --self-play --library rust/target/release/libtroll_farm.so \
  --output /tmp/rl-full-speed-native-4-f94be850.json
```

| Rayon threads / vector slots | full turn-steps | elapsed s | turn-steps/s | illegal |
|---:|---:|---:|---:|---:|
| 20 / 20 | 7,734 | 38.177046947181225 | **202.58245774483703** | 0 |
| 4 / 4 | 1,486 | 6.987314519006759 | **212.6711193489017** | 0 |

The speed result SHA-256 values are respectively
`145c51ca36f16617c7b1f4580069dddb8010b6d2fe4087aeea494059068396c4` and
`f65b394677b035a98f3376e938237d3a2cb2d604939ca7b7017213b0b7f17991`.
