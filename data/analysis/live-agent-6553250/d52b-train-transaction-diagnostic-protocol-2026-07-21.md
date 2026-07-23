# D52b TRAIN transaction diagnostic — frozen protocol (2026-07-21)

## Question

D52a creates crops in 100% of cells but reaches worker three in only 19.69%. The otherwise
post-funding producer-count parameter changes worker-three completion from 25.00% to 19.38% for
hp2 and from 22.50% to 11.88% for balanced. Source inspection identifies two ways a TRAIN that is
affordable at decision time can fail after higher-priority referee actions:

1. a worker remains on or moves onto the spawn shack before TRAIN; or
2. a preceding PICK removes PLUM, LEMON, APPLE, or IRON reserved by the TRAIN bill.

D52b measures this attribution without changing V3 commands or opening any value field.

## Frozen telemetry replay

Use the unchanged eight D52a V3 configs and unchanged strategy source on the same 160 consumed exact
maps. Add runner-only counters for each target workforce level (two, three, and four):

- TRAIN attempts and successful worker spawns;
- failed attempts with only the shack occupied after exact MOVE resolution;
- failed attempts with only the bill unaffordable after exact PICK resolution;
- failed attempts with both conditions; and
- failed attempts with neither condition.

The diagnostic prefix simulation may apply only the referee's exact MOVE and PICK semantics to a
clone. Other pre-TRAIN verbs cannot remove deposited TRAIN currency; the command parser permits at
most one unit command, so a PICK executor cannot simultaneously harvest, plant, or chop. Actual
success remains the authoritative before/after opponent-worker count around the full referee step.

Run one complete 160 x 8 matrix with 20 threads. Every pre-existing output field must match the
frozen D52a A row exactly after the new telemetry columns are excluded. Attempt counts must equal
successes plus the four mutually exclusive failure categories at every target level. Score,
coverage, distance, cohorts, opponent identity, and policy value are ignored.

Frozen inputs include:

- D52a A matrix SHA-256
  `47686b28222e92793414c7d50cb437c3e7d779f7f4f8b8bdf85a0ec0c2c66bae`;
- V3 strategy SHA-256
  `d13dea27b559e531d7fc53dc316768d2cb30e91e1064dd46f46c2e05fb645b78`;
- observed/map SHA-256 pair
  `c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.

## Decision rule

Pool failed attempts to workers three and four, where D52a collapses:

- if at least 80% include shack occupancy, the next scheduler must make spawn evacuation an atomic
  precondition of TRAIN;
- if at least 80% include post-PICK budget loss, it must reserve the exact current TRAIN bill
  through all higher-priority actions;
- if the union of those two causes reaches at least 80%, D53 may combine both invariants in one
  atomic TRAIN transaction even when neither cause alone reaches 80%; and
- if more than 20% remain unexplained, freeze a turn-level trace before any scheduler repair.

This diagnostic cannot promote a config, alter D52a's verdict, evaluate support, or authorize a
candidate, TestSession game, submission, or Arena action.
