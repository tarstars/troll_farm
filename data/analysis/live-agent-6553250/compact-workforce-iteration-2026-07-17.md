# Compact workforce residual iteration — 2026-07-17

## Outcome

**REJECT third-worker expansion from the promoted policy.**  The slim arena baseline remains
unchanged and no arena write was performed.  Two surplus-only candidates were behavior-inert;
two bounded funding candidates spent productive starter turns but never issued an additional
`TRAIN`.  The branch failed its discovery/activation gate, so untouched holdout and timing runs
were intentionally not consumed.

The experiment used the arena-validated 62,725-byte promoted source as the exact parent:
`candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`.

## Isolated candidates

| Candidate | Bytes | Mechanism | Seeds | Margin delta | Wood delta | W/T/L | Extra TRAIN |
|---|---:|---|---:|---:|---:|---:|---:|
| surplus duplicate | 62,725 | raise cap only; reuse the exact selected worker spec | 200 | 0 | 0 | 0/200/0 | 0 |
| surplus 2/2/0/2 | 62,886 | raise cap; use a cheaper fixed wood worker when already funded | 200 | 0 | 0 | 0/200/0 | 0 |
| starter-funded 2/2/0/2 | 63,056 | only the weak starter collects; trained worker keeps normal work | 60 | -2.225 | -1.092 | 19/3/38 | 0 |
| bounded starter-funded 1/1/0/1 | 63,071 | cheapest wood worker; stop the funding detour after turn 25 | 60 | -0.358 | -0.058 | 29/12/19 | 0 |

The unbounded funding branch lost 31.58 CHOP commands per paired seed on average.  The bounded
kill test reduced that damage to 1.28, but still never reached the intended training event.

Frozen candidate checksums:

- surplus duplicate: `a15d324fcb38473bbcce6168355629b2ad0cd5aae0ad2a97185ef2421c541009`;
- surplus 2/2/0/2: `5ef25a02af975d6f4e1070f72f436bbfae576f11395fbceec2e8f318241a9722`;
- starter-funded 2/2/0/2: `0139fd5aa22e9124eacfdbf6610990d173f0732fcacbde79ef68541de3662b4c`;
- bounded starter-funded 1/1/0/1:
  `ab3f87dcd6e98de45b710a72445ad400470ee88445a2df3ae97b06b6328a3623`.

## Behavior-neutral affordability telemetry

`surplus_workforce_study.py` ran 200 reused discovery seeds with 16 concurrent game workers.
All 400 sides trained their normal second worker at median turn 11.  From then through turn 280:

- zero sides ever afforded even `(1,1,0,1)`;
- its global closest state was one resource short;
- its median best total deficit was seven;
- median resource deficits at the best state, ordered PLUM/LEMON/APPLE/IRON, were `3/3/0/3`;
- the larger `(2,2,0,2)` worker had median best deficit 16.

The blocker is not APPLE or the source cap.  Normal play spends the opening economy on worker
two and does not replenish PLUM, LEMON, and IRON.  Funding worker three therefore requires a
new collection economy, while the corrected stall horizon usually ends the game before that
economy repays its lost chop turns.  This explains both the inert surplus variants and the
negative forced-funding variants.

## Consequence

Do not spend the new 37 KB headroom on a third-worker controller unless a genuinely different
resource-production mechanism first demonstrates payback.  The next compact residual should be
**renewal-only and TRAIN-free**: preserve the promoted Yamo/Orchard fallback, search only bounded
PICK/PLANT/HARVEST deviations in low-supply states, and require the simulated deviation to repay
itself inside the referee's current stall/grace horizon.  A rollout layer must use the actual
promoted policy as continuation; the GoldElite residual remains an architecture reference only.

## Integrity

- All four artifacts compile standalone with warnings denied and remain below 64 KB.
- Generator/focused telemetry tests pass.
- The generic paired study now accepts an explicit parent source, preventing accidental
  comparison against the pre-promotion exact-live artifact.
- No untouched seed block, arena submission, or submit-helper change was used for this rejected
  branch.
