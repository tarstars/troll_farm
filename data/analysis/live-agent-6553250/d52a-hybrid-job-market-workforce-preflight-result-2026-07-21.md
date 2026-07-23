# D52a hybrid job-market workforce preflight — result (2026-07-21)

## Verdict

**Reject this exact V3 job market before support evaluation.** It is deterministic, obeys its
opening and worker-cap contracts, creates a crop in every cell, and differs from its V2 parent in
876/1,280 cells (68.44%). It nevertheless reaches worker two in only 948/1,280 cells (74.06%),
worker three in 252/1,280 (19.69%), and worker four in only 4/640 eligible max-four cells (0.63%).

Score direction, field support, coverage, cohorts, opponent identity, candidate value, and every
platform outcome remain ignored. No support audit, candidate, TestSession, submission, or Arena
action opens from this result.

## Pre-execution amendment and integrity

An outcome-blind check of the already-frozen V2 parent file found that initial inventory affords
the hp2 TRAIN on only 46/160 maps and the balanced TRAIN on 71/160. Before any D52 run, the
impossible "TRAIN on every first command" wording was replaced by exact parent-conditioned TRAIN
presence and spec. No other threshold changed.

- Both 160 x 8 matrices contain 1,280 complete unique cells and are byte-identical.
- All 468 expected immediate TRAIN commands occur, with zero presence or spec mismatches.
- There are zero configured-cap violations and zero missing checkpoints.
- The two runs complete in 16.89 s and 17.79 s at 19.46 and 19.41 effective CPU cores.
- Four scheduler tests, fourteen runner tests, and four analyzer tests pass.

## Mechanism result

The max-three and max-four forms are identical through worker three, so the worker-two/three rows
below apply to both caps independently:

| First worker | Producer slots | Worker 2 | Worker 3 |
|---|---:|---:|---:|
| hp2 | 1 | 113/160 (70.63%) | 40/160 (25.00%) |
| hp2 | 2 | 113/160 (70.63%) | 31/160 (19.38%) |
| balanced | 1 | 124/160 (77.50%) | 36/160 (22.50%) |
| balanced | 2 | 124/160 (77.50%) | 19/160 (11.88%) |

Among max-four forms, hp2/one-producer reaches worker four three times, hp2/two-producer once, and
both balanced forms zero times. Every config creates at least one successful crop on all 160 maps,
so renewable asset creation passes while capitalization into workforce fails.

Every immediate opening TRAIN succeeds: 46/46 hp2 and 71/71 balanced cells reach worker two. Among
deferred openings, 67/114 hp2 and 53/89 balanced cells eventually reach worker two. The sharper
collapse occurs while funding the hybrid third worker.

## Multilevel interpretation

- **Representation:** procedural reassignment is real rather than an inert V2 rewrite; the 68.44%
  mechanism-change gate and 100% crop rate pass.
- **Workforce:** the architecture does not compose the D40 funding mechanism. Worker three falls
  below every 55% per-config floor and the 70% aggregate floor by a wide margin.
- **Role interaction:** one post-funding producer consistently beats two before worker three,
  although that parameter should matter only after a bill is funded. This localizes an interaction
  on the turn when TRAIN first becomes affordable.
- **Transaction ordering:** V3 sets `pending_cost=None` as soon as current inventory is affordable
  and immediately applies the post-funding role quota. Higher-priority MOVE/PICK actions then run
  before TRAIN in the referee. A new worker can remain on the spawn shack, or a producer can PICK
  reserved TRAIN currency, invalidating the command after the controller's affordability check.
  This is a source-level causal hypothesis, not yet a measured failure attribution.
- **Program:** changing worker specs, caps, producer counts, or gates on these consumed outcomes is
  ineligible. The next step is a telemetry-only replay that partitions failed TRAIN attempts into
  spawn-block, post-PICK budget, both, and unexplained causes without changing policy behavior.

## Gate result

Integrity, parent-conditioned opening, cap, crop, and trajectory-change gates pass. Both worker-two
gates, both worker-three gates, and both worker-four gates fail. Formal conjunction: **fail**.

## Evidence

- protocol SHA-256:
  `608ce2c166438da52171e788b6c2c7ca18908151ac3025eafda6a44a0859676d`;
- pre-execution amendment SHA-256:
  `4438d60f76d4adf800ab94bd684dbffbb642cf1d54ad873501aee25382fb9979`;
- repeated matrix SHA-256:
  `47686b28222e92793414c7d50cb437c3e7d779f7f4f8b8bdf85a0ec0c2c66bae`;
- activation result SHA-256:
  `fd46281e1a0011cbe0b04f11742d41cd086e44fc16f0cd143895bc735eeac5d6`;
- runner SHA-256:
  `fb6c66f8cdcfa7d76b9309a4d05ae7d02c91733ea1e40516cbf6985294be92d1`;
- strategy SHA-256:
  `d13dea27b559e531d7fc53dc316768d2cb30e91e1064dd46f46c2e05fb645b78`;
- analyzer SHA-256:
  `1712caf64253fcbdc95dafbe1da5f5aa08bdb4e234609d86ce1f20bbfb2fd62e`.
