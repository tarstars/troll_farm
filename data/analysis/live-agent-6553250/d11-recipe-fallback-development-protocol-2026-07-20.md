# D11 recipe-7 funding fallback — development protocol (2026-07-20)

## Hypothesis

Recipe 7's full-game advantage can be retained while eliminating its funding deadlocks by
switching the unbuilt target to recipe 6 at a fixed turn.  Once recipe 7 has trained, no switch
is allowed.

This is a second development pass on the already reused seeds 0--7.  It may select one
prospective hypothesis, but cannot promote a candidate or authorize Arena activity.

## Frozen implementation

- Start target: recipe 7, `2/3/1/2`.
- Fallback target: recipe 6, `2/2/0/2`.
- At the start of turn `D`, before observation/inference, replace the target only if the original
  worker is still unbuilt.
- Preserve actor recurrent bookkeeping, crop provenance, observation construction, and every
  other V5 behavior.
- Research V6 source:
  `curriculum-level5-seed-reacquisition-d11-live-v6-recipe7-fallback-research.rs`, 69,377 bytes,
  SHA-256 `443c06e68ad1321224a001f0371a7084e5b2d0e8be89b3f122c7e0f1c09aff75`.
- Research V6 binary SHA-256:
  `14092cd5b0f23736c4973e42174ce40f79c2181cb0af549f9364d50fec0866b8`.

With no `--fallback` argument, V6 matched V5 on all 16 non-timing fields streams in the seed-0
resident smoke catalog.  A fallback smoke test confirmed that a deadline-40 switch trains the
recipe-6 worker, while a recipe-7 worker built before deadline 60 remains recipe 7.

## Sweep

- Deadlines: turns 40, 60, 80, 100, 120, 150, 180, and 210.
- Maps, seats, and opponents: exactly the 96 seed/seat/opponent cells in the fixed-recipe
  development catalog.
- Games: 96 × 8 = 768.
- Parallelism: 20 independent games.
- Fixed controls: reuse the deterministic recipe-6 and recipe-7 rows from the completed catalog.

The deadline grid spans before median recipe-7 completion, its interquartile boundary, its p90,
and its observed late tail.  These thresholds were chosen after the fixed catalog and are
therefore discovery-only.

## Primary analysis

For each deadline report:

- map-balanced margin and delta from fixed recipes 6 and 7;
- mean delta by opponent and the worst opponent mean;
- final worker spec and training-completion rate;
- fallback activation rate;
- performance in the five known recipe-7 failure cells;
- performance in cells where fixed recipe 7 trained successfully, measuring the opportunity cost
  of switching too early.

## Frozen selection rule

A deadline is eligible only if all conditions hold:

1. 96/96 games train a second worker;
2. map-balanced mean margin is at least 5 points above fixed recipe 6;
3. no opponent mean is more than 5 points below fixed recipe 6;
4. mean margin is not below fixed recipe 7;
5. the mean delta from recipe 6 is positive both in the five failure cells and in the 91 cells
   where fixed recipe 7 trained.

Among eligible deadlines, select the highest map-balanced mean.  If multiple deadlines are
within one point, select the earlier deadline.  If none is eligible, close fixed-deadline fallback
and retain recipe 6 as the integration fixture; do not tune the gates after seeing results.

## Outputs

- row data: `d11-recipe-fallback-development-seeds0-7.tsv`;
- analysis: `d11-recipe-fallback-development-2026-07-20.json`;
- result: `d11-recipe-fallback-development-result-2026-07-20.md`.

