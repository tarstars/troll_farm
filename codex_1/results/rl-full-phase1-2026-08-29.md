# Full-game neural environment Phase 1 — amended implementation and gates

Implementation source commit: `f0b50c7704c7e778a0b57167721d8172741458e4` on
`agent/codex_1`; the exact staged-MOVE routing sentence is at
`74ad13707422fb2e3c884e81bcf00bc8e4f24c9a`. No Arena action was taken. The byte-sacred
resident remained
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Delivered surface

- `rust/src/rl_full.rs`: the signed `v400-2026-08-29` plan vocabulary, seat- and
  active-cell-aware codec, strict staged-prefix state reconstruction, executing-step-only reward,
  real command-rejection audit, exact terminal metadata, persistent PPO target, real-map episode
  construction, seven opponent modes, Rayon batches, and the `tf_full_*` C ABI.
- `cgauto/rl_full_env.py`: the exact `rewards, info = env.step(actions)` surface with named
  `FullStepInfo` arrays, NumPy/ctypes vector wrapper, legal random sampler, initial-state replay
  reconstruction, and independent transition and terminal parity checks through `sim/engine.py`.
- `tests/test_rl_full_env.py`: ABI, version, shape, both-seat codec, 10,000 masked-action,
  200-replay, initial-state, truncation, post-terminal, and mutated-terminal negative controls.
- `local_claude_1/nn-bot/OBS-PLANES.md` and `ENV-API.md`: signed 400-entry vocabulary,
  widened talent/cost scales, exact staged MOVE tie/unreachable semantics, strict reconstructed
  context, terminal replay schema, and the final Python step contract.

The amendment-specific negative controls prove that rejection accounting can become nonzero, that
terminal parity detects a changed reason and stall counter, and that a transition appended after a
valid terminal is rejected. The plan mask exposes all 400 entries when capacity permits and only
entry 0 when it does not.

## Native build and focused tests

The repository-native release library was built from the final source with:

```text
/home/tarstars/.cargo/bin/cargo build --manifest-path rust/Cargo.toml --release --lib
```

`rust/target/release/libtroll_farm.so` is 3,491,648 bytes with SHA-256
`bb2d2ae93cf01c6a0ee91143b9187f976c53336416b3ac03d80804edb836d1ea`.

The native Python suite ran as:

```text
TF_FULL_TEST_LIBRARY=/home/tarstars/prj/troll_farm-codex_1/rust/target/release/libtroll_farm.so \
  /home/tarstars/.local/bin/uv run --with numpy pytest -q tests/test_rl_full_env.py
```

Result: **7 passed in 375.07 s**. This includes 10,000 accepted random masked learner actions,
**200/200** no-train self-play replays, both seats and all 13 verbs through the C ABI, chop-zero
initial-state mutation, truncated replay, valid post-terminal append, and mutated terminal
reason/counter controls.

A focused release harness importing the exact production `state.rs`, `engine.rs`, strategy
sources, byte-sacred resident source, and `rl_full.rs` ran the amended module tests:

```text
/home/tarstars/.cargo/bin/cargo test --release \
  --manifest-path /tmp/troll-full-check.iGsiu8/Cargo.toml \
  --lib rl_full::tests -- --nocapture
```

Result: **9 passed in 31.67 s**. The repository-native library also passes `cargo check --lib`.
The focused harness remains necessary because this worktree's unrelated `rl_q6_proposal` test
module names a historical compile-time TSV under unavailable bulk storage; no replacement dataset
or symlink was created. The exact 415 MiB harness was removed after the tests completed.

## Required fresh 1,000-game gate

The fresh amended gate uses fully random legal actions on both seats, real maps, exact transition
and terminal replay verification, 20 vector slots, and four Rayon threads:

```text
PYTHONPATH=. RAYON_NUM_THREADS=4 /home/tarstars/.local/bin/uv run --with numpy \
  python cgauto/rl_full_env.py --episodes 1000 --num-envs 20 --seed-base 320000 \
  --self-play --verify-replays --library rust/target/release/libtroll_farm.so \
  --output /tmp/rl-full-gate-v400-ecb73ea5.json
```

| measure | result |
|---|---:|
| target episodes | 1,000 |
| exact seed interval | 320000–320999, 1,000 unique |
| transition parity | **1,000/1,000** |
| terminal parity | **1,000/1,000** |
| illegal commands | **0** |
| terminal turns | 300 min / 300 max |
| wins | 411 |
| unique action hashes | 1,000 |
| unique terminal state hashes | 1,000 |
| learner mini-steps emitted | 895,900 |
| full turn-steps executed, including batch overshoot | 302,201 |
| elapsed | 2,465.753302715253 s |
| full turn-steps/s, including independent replay verification | 122.5593005055374 |

The 232,260-byte raw result SHA-256 is
`5e1a27ab1d73654c02995eb336b483dbd679039757b7b7ffc3f03d9f6ce7b810`. The timing-independent
SHA-256 after removing
`elapsed_seconds` and `turn_steps_per_second` and serializing with sorted keys and compact JSON
separators is `8ae5a0098ff3bf27ecc8de4d3dad8bd3aaa5070bfe37273b366706d3412618de`.

## Speed lines

The VM evidence uses four Rayon threads and four vector slots without replay verification:

```text
PYTHONPATH=. RAYON_NUM_THREADS=4 /home/tarstars/.local/bin/uv run --with numpy \
  python cgauto/rl_full_env.py --episodes 4 --num-envs 4 --seed-base 330000 \
  --self-play --library rust/target/release/libtroll_farm.so \
  --output /tmp/rl-full-speed-v400-4.json
```

| Rayon threads / vector slots | full turn-steps | elapsed s | turn-steps/s | illegal |
|---:|---:|---:|---:|---:|
| 4 / 4 | 1,218 | 5.685295050963759 | **214.23690223316152** | 0 |

Speed result SHA-256:
`5cfe71c3307fb217e9b1bc74789baf4b54af8fbdf97a1cdfb5e4264da9985a85`.

For context only, a shared-load 20-slot probe completed 11,712 turn steps in
106.63313338626176 s (**109.83452917560925 turn-steps/s**) with zero illegal commands. It is not
presented as the four-core VM speed line.

## Superseded evidence

The earlier `f94be850` 1,000-game run and its 6-test/144-vocabulary surface are build progress only,
not Phase 1 closure. They predate amendments 1–9 and are explicitly superseded by the fresh gate
above. In particular, their single `replay_parity` field cannot substitute for the separate
transition and terminal checks, and their constant-zero rejection field cannot substitute for the
audited counter with a nonzero negative control.
