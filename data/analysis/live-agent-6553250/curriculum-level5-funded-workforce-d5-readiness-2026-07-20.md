# Curriculum Level 5 naturally funded two-worker D5 readiness — 2026-07-20

## Verdict

**Ready to open the frozen development bank 2,500--2,999.**  The exact D5 opponent contract is
implemented without changing player-0 observations, action masks, task, reward, checkpoint, or
episode horizon.  It trains at most one ordinary `(2,2,0,2)` opponent chopper, and every observed
training follows a state-confirmed external funding receipt.

## Integrity evidence

- `cargo test --manifest-path rust/Cargo.toml --release --lib rl_level3::tests`: **12 passed**;
- `.venv/bin/pytest -q tests/test_rl_level5_env.py tests/test_train_level1_ppo.py`:
  **20 passed**;
- identical D5 batches reproduce every observation, mask, reward, and old/new terminal field;
- all existing Level-5 modes pass after the common terminal ABI grows from 23 to 26 pointers;
- the trained unit is asserted to have exactly `(2,2,0,2)` talents;
- every in-episode roster assertion is <=2 workers and every destruction assertion is <=1; and
- training turn, funding receipts, and trained-worker productive actions are terminal telemetry
  only and never enter the actor observation.

The first Python test invocation used the just-rebuilt Rust test binary with the previously built
shared library.  Existing modes therefore left the three new buffers uninitialized and the new
symbol was absent.  Rebuilding `libtroll_farm.so` resolved the ABI mismatch; the unchanged suite
then passed 20/20.  No experimental seed was opened by this build-order defect.

## Consumed-seed implementation readiness

One deterministic teacher replay on already-consumed seeds 0--499 verifies material activation;
it is not a D5 gate and did not change the frozen opponent or thresholds.

| Measure | Consumed result |
|---|---:|
| Teacher overall / nontrivial | **100% / 100%** |
| Worst recipe / height | **100% / 100%** |
| Player crop / renewable harvest | **100% / 100%** |
| Illegal selected actions | **0** |
| Opponent training rate | **95.40%** |
| Median opponent training turn | **15** |
| Trained with verified funding receipt | **100%** |
| Trained-worker productive activation | **92.40%** |
| Maximum opponent workers | **2** |
| Opponent crop / own-crop harvest | **92.80% / 79.40%** |
| Confirmed player-crop destruction | **91.60%** |
| Mean trained-worker productive actions | **22.052** |

This verifies that D5 is not an accidental one-worker or idle-second-worker control.  Compared
with D4 it activates a delayed, paid workforce transition and sustained parallel work while the
teacher remains feasible.  The fresh result remains unknown and controls the decision.

## Execution authorization

Run teacher and random legal once on exactly seeds 2,500--2,999 under the frozen protocol.  Actor
replay is conditional on both controls passing.  No learning, prospective bank, YT operation,
deployment, or Arena action is authorized yet.

## Execution anchors

- D5 protocol:
  `37c8f4ca00d247a16b55db4fa16b1aea80aac0471320c257ab9273efa9da7b52`;
- consumed readiness artifact:
  `4e917379e92e410d80fb7a4991c28abc1a9ac0050227b81629ac63833ecf86d8`;
- Rust source:
  `09b201e5b388e7d2391463670c0c9116289866a71caf94e5c13837b4bdf5521b`;
- Level-5 Python environment:
  `c35a43f2061ed02b5e54e910f43b0dc9861af3a872c4d2625f0358ea42a193a8`;
- PPO/evaluation environment selector:
  `05a12c066e6542b055937d7ccac99dbfb5528edc7bad8c07784c7ac31b9a924c`;
- Level-5 checkpoint evaluator:
  `9aa14c738c2b95873dd59c408f148e28307b52c3fd9f157a671782dd583a4920`;
- focused Python tests:
  `4532871b63cf7f894c3dffc4b6ccd3f0770c3eed70a4eeb385ac56d9c2dac566`;
- release shared library:
  `1d1752d8681302e1e7006ea82cd7338f56c8e36c4767c3ba9b1d78ae9bf4dd38`; and
- accepted Level-4 checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`.
