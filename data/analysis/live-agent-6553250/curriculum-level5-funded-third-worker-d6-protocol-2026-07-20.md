# Curriculum Level 5 naturally funded third-worker D6 protocol — frozen 2026-07-20

## Question

Does scaling the accepted paid two-worker economy through a second natural funding/training epoch
and a productively active third opponent worker cause a new control failure?

D5 prospectively rejects “more than one worker” as a binary explanation: its unchanged actor solves
97.85% while the paid second worker is productive in 92.95%.  The complete D0 opponent can grow
beyond two.  D6 changes workforce scale by exactly one while retaining bounded roles and one
tracked player-crop destruction.

## Frozen opponent

The first transition is byte-semantic D5: one ordinary starter obtains an external funding receipt,
pays the ordinary one-worker cost for `(2,2,0,2)`, and creates the standard chopper.  A successful
training transition resets the funding-epoch receipt.  No later `TRAIN` is legal until the starter
has harvested or mined, banked at least one new external cost item after that transition, and the
bank can pay the full ordinary two-worker cost for a `(1,1,1,0)` feeder: 3 PLUM, 3 LEMON, 3 APPLE,
and 2 IRON when iron exists.

While the roster has two workers, the starter gathers/banks third-worker deficits and the standard
chopper retains the D5 one-shot player-crop reaper plus initial-natural-plant chopper role.  After
the feeder is trained:

- the original starter follows the regenerative-planter lifecycle;
- the standard chopper retains its bounded D5 role; and
- the feeder deterministically harvests natural fruit and banks it, using no `PLANT`, `CHOP`,
  `PICK`, or `TRAIN` command.

Training is permanently disabled at three workers.  No inventory, talent, unit, score, crop,
cooldown, or position is gifted or edited.  Player 0 retains the exact D2/D4 lifecycle, supplied
recipe, actor inputs, action mask, reward, checkpoint, 240-turn horizon, and success definition.

## Telemetry and implementation integrity

Terminal-only telemetry must additionally expose:

- first and third-worker training turns;
- successful funding-backed training-event count;
- confirmed productive actions separately for the standard chopper and feeder; and
- final/max workforce through the existing roster field.

Before fresh execution, deterministic consumed-seed tests must prove:

- the first and second training transitions each require a fresh post-previous-training receipt and
  ordinary affordability;
- the roster never exceeds three and both trained specifications are exact;
- the standard chopper and feeder each produce confirmed role-appropriate actions;
- no episode records more than one tracked player-crop destruction;
- all D1--D5 modes and terminal fields remain deterministic; and
- the observation/action contract remains 104x11x22 and 13x11x22.

Implementation diagnosis may use only already-consumed seeds 0--2,999.  The commands, thresholds,
fresh interval, checkpoint, or player policy may not be tuned from those outcomes.

## Fresh D6 development controls

Run teacher and random legal exactly once on seeds 3,000--3,499 with 100 environments, a 240-turn
horizon, and random seed 89.  Teacher must reach:

- >=85% overall and >=82% nontrivial success;
- >=75% in every recipe and >=80% in every height;
- >=80% player-crop presence and >=85% renewable harvest;
- zero illegal selected actions;
- first-worker training in >=90% and third-worker training in >=55% of episodes;
- a verified fresh funding receipt before 100% of both first and third-worker training events;
- confirmed standard-chopper productivity in >=75% and feeder productivity in >=45% of episodes;
- exactly three terminal opponent workers in every recorded third-worker training episode, never
  more than three;
- >=45% opponent crop creation, >=15% opponent own-crop renewable harvest, and >=60% confirmed
  player-crop destruction; and
- no episode above one tracked player-crop destruction.

Random legal must remain <=5% overall.  Failure stops D6 before actor replay, learning, prospective
seeds, deployment, or Arena action.

## Fixed-actor gate

If controls pass, replay the unchanged accepted Level-4 checkpoint exactly once on the same seeds
against the exact teacher artifact.  It must reach:

- >=75% overall and >=72% nontrivial success;
- >=65% in every recipe and >=70% in every height;
- >=75% player-crop presence and >=80% renewable harvest;
- paired-teacher median completion delay <=30 turns; and
- the same training, fresh-funding, two-role productivity, workforce-cap, opponent-crop, harvest,
  and destruction gates as the teacher.

A pass permits one separately frozen prospective confirmation without learning.  A feasible
teacher plus actor failure permits diagnosis and a separately frozen learning protocol.  Neither
outcome authorizes source integration or Arena submission.

## Compute decision

D6 controls remain a seconds-scale local workload.  YT remains deferred unless this experiment
authorizes a multi-million-transition clone/PPO cycle, in which case a frozen 100,000-transition
local-versus-YT-GPU benchmark precedes the full run.

## Pre-implementation anchors

- accepted D5 prospective result:
  `80e2c3aa7f2cf5d8654d0da6cb2dce2368cc30967278505ac12d4803dacb6acf`;
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
