# Curriculum Level 5 seed-reacquisition expert D11 readiness — 2026-07-20

## Verdict

**Ready for the single frozen fresh control execution on seeds 6,000--6,499.**  D11 repairs the
expert's empty-seed absorbing state while preserving the exact D10 task exposed to external
actions.  Consumed teacher/random are 99.40%/0% and every future mechanism floor has healthy
headroom.

## Integrity evidence

- Feeding identical external actions into D10 and D11 produces byte-identical observations,
  masks, rewards, and terminal telemetry through completion and automatic reset.
- D11 teacher labels diverge only after the target is built and the active farmer has no crop, no
  carried item, and no home banana inventory.
- The fallback uses the existing real-source selector; no inventory or plant is created.
- D10 retains the frozen non-reacquiring teacher.  D9 and all earlier modes retain their horizons
  and one-destruction limits.
- Crop-before-scale, two fresh funding receipts, cap three workers, cap three destructions, and
  deterministic behavior remain enforced.
- Fourteen focused Rust Level-5 tests and thirty-two Python PPO/Level-5 tests pass.  Python
  byte-compilation and release compilation pass; the only build messages are four pre-existing
  warnings outside `rl_level3.rs`.

## Consumed readiness bank

Actual FFI teacher and random legal were run on consumed seeds 0--499 with 100 environments,
timeout 240, and random seed 113.

| Measure | Teacher | Random |
|---|---:|---:|
| Overall / nontrivial success | **99.40% / 98.98%** | **0% / 0%** |
| Worst recipe / height | **94.64% / 98.40%** | 0% / 0% |
| Terminal crop / renewable harvest | **99.40% / 99.40%** | 2.40% / 0.20% |
| First / third-worker training | **100% / 98.00%** | 100% / 99.00% |
| Fresh first / second receipt | **100% / 100%** | 100% / 100% |
| Chopper / feeder productivity | **100% / 93.80%** | 100% / 96.20% |
| Rival crop / own renewable harvest | **100% / 91.20%** | 100% / 94.40% |
| At least one / two / three destructions | **100% / 98.40% / 96.20%** | 16.60% / 2.20% / 0.20% |
| Maximum destructions / workers | **3 / 3** | **3 / 3** |
| Illegal selected actions | **0** | **0** |

Relative to the frozen D10 teacher on the same bank, the expert gains 12.8 percentage points of
success and 6.8 points of three-contact activation.  That direction excludes pressure avoidance
as the source of the gain.

## Frozen execution rule

Run teacher and random exactly once on `[6000, 6500)`.  Evaluate every frozen control gate before
opening the fixed actor.  A control failure closes D11.  A full control pass opens exactly one
fixed-actor replay against the teacher artifact; it does not itself authorize learning, YT writes,
prospective access, deployment, or Arena action.

## Reproducibility anchors

- protocol: `fd91ab60be78fb5253f275be56e4b93a1828081aacf624d4c863f2529a3dda96`;
- consumed teacher: `dca1706885c8d4bef5e5ab18dbdc55e7eb5f753767fb81621d5b68427f3feece`;
- consumed random: `96952d9855b7f7a789c9b61e9a0c70dd6c6bc512588d57001f89dddeff3ca0cd`;
- Rust source: `245fd4c8cd48861d40a7a600f65527c6b88fa53a22dc55f00ce5b5196d9555f6`;
- Level-5 environment: `29328f0b614c6d57ccee4bae2a962815ec2d9cc281eaabcc9b34943a90d1331c`;
- PPO/evaluation selector: `012fdd132dbee19b0e968aa2f80f46127de3c7e9e16e7256c1b9a539ebf8fb49`;
- evaluator: `6ca711a65be6164e9a0dd3ce3242b68b53e7780ef18e1cbd950d300e6f2ba052`;
- focused tests: `f4056853d8a5df06b97f0dda98fd217be462042f832c141061fc681fb78df9d1`;
- release library: `381ba5623afb13d77fed09a80dbc2fabc0dd483781a56e9f3c65477783a1dab7`;
  and
- fresh interval: `[6000, 6500)`, unopened at readiness freeze.
