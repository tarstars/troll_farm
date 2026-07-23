# Field economy-catalog calibration smoke — frozen protocol, 2026-07-19

## Question

Can any of the already-frozen 31 complete-economy configurations reproduce the macro trajectory
of the three largest Legend archetypes missed by the old continuation zoo when each runs against
exact `b100_e6` on the same official initial map?

This is opponent-model reconstruction, not candidate tuning.  A farm config is placed on the
opponent side solely as a field proxy.  Its old candidate-performance result is not reopened, and
this smoke cannot qualify a candidate or authorize arena work.

## Immutable inputs

- The 160 normalized official maps and observed signatures from the completed field-continuation
  audit, map SHA-256
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.
- Exact formatted `b100_e6`, constructed as
  `SecureOrchardBot::opponent_crop_priority(100, 6, 1, 1)`, always local player 0.
- The exact 31 nonresident configs frozen in
  `complete-economy-representation-smoke-protocol-2026-07-19.md`.  Do not add, remove, or tune a
  config after observing results.
- The old eight-model coverage matrix as the baseline union.
- The same referee, terminal rule, event counters, 24 feature tolerances, terminal tolerance,
  `macro_covers`, and `fully_covers` definitions frozen in
  `field-continuation-coverage-protocol-2026-07-19.md`.

Run all 31 configs on all 160 maps: 4,960 exact-map trajectories.  Use 20 workers.  No generated
seed, controlled platform game, submission, source packaging, or live agent is permitted.

## Frozen calibration split

Assign each game independently from its immutable ID:

`SHA256("field-economy-calibration-v1:" + decimal_game_id)[0] & 1`

Bucket zero is discovery and bucket one is confirmation.  The analyzer must report cohort and
critical-subcohort counts before reporting model outcomes.  Both partitions are consumed replay
diagnosis data; the split only prevents choosing a representative and judging it on the same
maps.

## Target archetypes

Use the audit's deterministic labels, unchanged:

1. `rich3plus:farm_wood:train_now`;
2. `compact2:farm_wood:deferred`; and
3. `compact2:wood_only:deferred`.

For each archetype on discovery, rank every config by:

1. more games macro-covered by that single config;
2. more games fully covered;
3. lower mean normalized macro distance; and
4. lexicographic config label.

Nominate the first config for that archetype.  Deduplicate identical winners, yielding at most
three unchanged representatives.  Selection does not use confirmation outcomes.

## Frozen confirmation gates

Let the expanded suite be the old eight-model union plus all nominated representatives.  The
catalog is a useful representation basis only if every applicable check passes on confirmation:

1. the exact 160 x 31 grid is complete, unique, and has all checkpoints;
2. expanded macro coverage improves over the old zoo by at least 10 percentage points overall;
3. expanded full coverage improves by at least 5 percentage points overall;
4. expanded macro coverage improves by at least 15 percentage points in catastrophic games;
5. expanded macro coverage improves by at least 15 percentage points in worker-rich games; and
6. for each target archetype having at least four confirmation games, its discovery-nominated
   representative macro-covers at least 20% of that archetype's confirmation games.

Rates are calculated within the confirmation partition and compared as unrounded proportions.
If a critical confirmation cohort is empty, its check fails rather than being waived.

Also report exact-opening and full-coverage changes for each target archetype.  These are
diagnostic: if all macro gates pass but full coverage fails primarily from opening mismatch, the
next eligible experiment is a frozen opening-spec graft onto the selected controller.  Do not
change openings inside this smoke.

## Stop and continuation rules

- **All gates pass:** retain the selected configs only as field-calibrated opponent models, rerun
  the global support audit, and then construct a fresh policy-evaluation ambiguity set.  Do not
  resurrect a farm config as our candidate.
- **Macro gates pass but full/opening gates fail:** keep only the macro representation finding and
  test a separately frozen opening overlay.
- **Any macro or archetype gate fails:** close parameter-only calibration of GoldElite.  The next
  opponent proxy must be structurally new, with replay-derived harvest-capable worker training and
  role allocation rather than another workforce/hold/farm-cap sweep.
