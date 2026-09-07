# H10a pre-authorization readiness — 2026-09-01

## Outcome

The complete local pipeline passed pre-authorization review. On 2026-09-01 the owner gave standing
permission: **“Publish any candidate that passes all frozen offline gates; no additional approval
is required.”** Full tensor export, model fitting, held evaluation, and platform publication are
therefore enabled. No model or candidate existed when authorization was recorded.

## What is implemented

- Compose-only Rust map encoder over the frozen D172a control states.
- Exact corpus/state integrity check with transparent handling of the archive's one nine-decimal
  float round-trip.
- Deduplicated tensor materializer with `/data` path enforcement, temporary-file publication,
  fixed-size checks, sorted state keys, and overwrite refusal.
- Frozen 6,541-parameter Python model and state-batched trainer.
- Matching Rust weight loader and inference implementation.
- Closed-loop, one-use Rust evaluator preserving the 13 arms and `+1.0` threshold.
- Selection, veto, and one-use confirmation analyzer with the unchanged D172a gates and tie-break.
- Independent authorization guards for model fitting and held evaluation.

## Verification

- Full compose-only replay: 79,997 archived rows, 27,392 states, no missing/extra rows, no tensor
  shape/orientation/repeated-state errors. The sole raw float-bit difference is `1/300`; it matches
  the archive's exact nine-decimal format.
- Tensor smoke export: 51 states, 888,624 bytes, expected `51 × 72 × 11 × 22` layout.
- Trainer self-test: exactly 6,541 parameters; invalid padded cells change logits by exactly `0`.
- Input join smoke: 153 decision rows joined to all 51 smoke states.
- Python/Rust inference parity: all 13 scores matched with maximum absolute difference
  `1.536560059745007e-8`; tensor fingerprint matched.
- Analyzer self-test: admission boundary passes; each of six single-gate failures is rejected;
  the frozen tie-break selects lower seed `101001` when all value statistics tie.
- Authorization tests: attempted fitting and held evaluation both failed before creating output.
- Rust suite: 9 passed, 0 failed, including the exhaustive D172 arm-offer/activation agreement
  check (`769.13 s`).
- Frozen D172a source remains SHA-256
  `219f7de187988437871551e1b15cd585a5de2514a6927ad07142c4713d35a295`.
- Main repository status remains only the pre-existing `M data/processed/stats.json`.

## Source and executable hashes

| Artifact | SHA-256 |
|---|---|
| `build_h10a_spatial_exporter.py` | `7a8b1ef813eee4914587545d1081cd0042fb73aa083ccd3243c899ba0d200d20` |
| `train_h10a_spatial_selector.py` | `07508f300a5dfbd70c842eacfb054caf096b653c9867174dba10e906091e91de` |
| `analyze_h10a_spatial_selector.py` | `1697642a414bdaed3eb4eb889fcb7417596a6f6a1e7d4a0168f183dc643a4906` |
| `H10A_SPATIAL_TRAINING_PROPOSAL.md` | `d3993e4b83b053ebd6e27a1eebbe658bd0c35d31765b0a314e11691ed6a84fdf` |
| `H10A_SPATIAL_TRAINING_LOCK.json` | `eb6c9981f200303c07cc1b54011df1b3714f84c6a489e82fd94e062081e0efc2` |
| generated Rust source | `16f6462095643fd97a82625fa3a955e85441ad10abd8d921f19d0a40ca48de11` |
| release evaluator | `71df6a2e291ff11f327ab8e6d945b4fd3b974d4cea5a59cc0feb578b257dd91c` |

## Evidence hashes

| Evidence | SHA-256 |
|---|---|
| trainer self-test | `6525fe93b58e8f7485dd24266ecfe16e9e3d1ca79e7dbeb36d977aaece847f89` |
| trainer input smoke | `5eeb042d4ed3e695f702dab2b847f20c675e91e243655bff64a58450b6de6d99` |
| analyzer self-test | `52615200c08234f2a6e8016869ba17b45fc00afa2faaa9de841c1536321297c0` |
| Python/Rust inference parity | `46fb5be627e0bdbef0a8f793792666ffb62f651ceb689e5c7332d3624ad9c638` |
| smoke state index | `96d7e9480033d84a4f4f0950f616d8a752ac09d57119f0206bbb30cebbaf8b22` |
| smoke tensor bytes | `1f371651d2b2c045667dabf4f3db968f51928480c45006148c1f56be5a42bb47` |

## Next authorized sequence

Authorized execution sequence:

1. Rebuild and hash-check the exporter.
2. Materialize all 27,392 training tensors under
   `/data/separate_troll_farm-working/experiments/h10a-spatial-selector/`.
3. Require a full 79,997-row input join.
4. Fit seeds `101001` and `101002` once each.
5. Evaluate both on the frozen eight-block selection range.
6. Stop if neither is admitted. Otherwise run veto once, then open confirmation once only after a
   veto pass.
7. If confirmation passes, construct and publish the candidate without another approval, then
   monitor all 160 games and ranking stabilization.
