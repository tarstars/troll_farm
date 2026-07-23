# Curriculum Level 5 sustained funded-trio D8 readiness — 2026-07-20

## Readiness verdict

**Ready for the single frozen fresh control execution on seeds 4,000--4,499.**  The separate
turn-180 mode is implemented and validated using only consumed seeds 0--3,999.  No fresh D8 seed
has been opened, and no protocol gate changed after readiness results.

## Implementation integrity

- `FundedTrioSustained180` is a distinct Rust opponent mode with `min_success_turn = 180`.
- The prior `FundedTrioSustained` mode remains fixed at turn 120.
- Both modes call the exact same `funded_trio_commands`; D8 has no economic, role, telemetry,
  observation, mask, reward, milestone, or timeout difference.
- The D8 FFI and Python wrapper preserve the 104x11x22 observation and 13x11x22 action contract and
  the existing 29-argument terminal ABI.
- The evaluator and accepted-checkpoint path select `funded-trio-sustained-180` explicitly.
- Fifteen focused Rust tests pass, including deterministic turn-120 and turn-180 mode separation,
  legality, two funding epochs, role talents, cap three, and bounded destruction.
- Twenty-six focused Python tests pass, including byte-identical D8 batches, no terminal before
  turn 180, and preservation of the earlier turn-120 summary.

The Rust build reports only four pre-existing warnings in unrelated strategy files.

## Consumed smoke results

Teacher on seeds 0--499:

- 500/500 overall and nontrivial 295/295;
- 100% in every recipe and height;
- 100% player crop and renewable harvest, zero illegal selections;
- every success at median turn 180 and none before 180;
- 100% first-worker training and 96.00% third-worker training;
- 100% fresh funding attribution for both transactions;
- 100% standard-chopper and 89.60% feeder productivity;
- maximum three opponent workers;
- 81.00% opponent crop creation, 65.80% opponent own-crop harvest, and 99.80% confirmed
  player-crop destruction; and
- no episode above one tracked destruction.

Random legal on consumed seeds 0--99 with random seed 97 is 0/100.  The opponent reaches three
workers in every episode and remains materially active.  This is a discrimination check only, not
fresh evidence.

The 81.00% crop-creation and 65.80% harvest rates clear the already frozen 80%/65% fresh floors
narrowly.  They are therefore evidence that D8 is executable, not grounds to alter either floor.

## Frozen execution

Run exactly once, locally, with 100 environments and a 240-turn timeout:

1. teacher on seeds 4,000--4,499;
2. random legal on the same seeds with random seed 97; and
3. only if every protocol control passes, the unchanged accepted Level-4 actor on the same bank
   against the exact teacher artifact.

Any failed control closes D8 before actor replay.  No learning, YT, prospective, deployment, or
Arena action is authorized by readiness alone.

## Frozen anchors

- protocol:
  `a38d899798c60feed4cec5085588b6373e6523a18301a938506a9bfdd9403d07`;
- consumed teacher artifact:
  `af39cf0b475a45e0541d92bf9ff7aa354bb431af4e14b1b6ff4ed3fbf9f7b6d7`;
- consumed random artifact:
  `567adfc36186330564ba58b843b842b39037dc50e886ae14b1d8d230e37dbc63`;
- Rust source:
  `fbda7052ca1bdf842dbadc32bb0fcf619b89b4cee79d680255e5ecead29946e4`;
- Level-5 Python environment:
  `6791307e5a32a6850be593d12a0c73678a683c99c427ace06a86762ce74989a0`;
- PPO/evaluation selector:
  `4984e20ed6002f4c6f9b87c48e19e53f792f1401e42d4bcbfe16b903aec85a99`;
- Level-5 evaluator:
  `9664da43483b3b0a2cb5585ce92ac7fa02b7ededde2a401efe3604d5f6b8c034`;
- focused Level-5 tests:
  `71d3c4415c58cb6968dcc21a98f95e43d68d7c05e4984e7982c4e44beb34ef34`;
- release shared library:
  `a4ce9d5460afc13fa2e288e7b9cdd15198481daa877db975b2b38fe114facf81`;
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`; and
- fresh seed interval:
  `[4000, 4500)`, unopened at this freeze.
