# Field economy-catalog calibration smoke — result, 2026-07-19

## Verdict

**Close parameter-only calibration of GoldElite.**  The frozen catalog adds useful representation
for compact two-worker economies, but it fails every critical-cohort gate and completely misses
the immediate rich farm+wood family on confirmation.  More workforce, stagger, hold, or farm-cap
tuning within this controller is not the next move.

This remains opponent-model diagnosis.  No farm config is reopened as our policy, and no fresh
seed, arena game, submission, resident source, or live agent was touched.

## Integrity and split

- 160 exact official maps x 31 frozen configs = 4,960 unique complete trajectories.
- Exact `b100_e6` was local player 0 in every cell; the map dataset SHA remained
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.
- All turn-50, turn-100, final, opening, and terminal fields were present.
- The precommitted SHA-256 split yielded 80 discovery and 80 confirmation games.
- Discovery/confirmation critical counts were 12/19 catastrophic and 23/28 worker-rich.
- Target archetype counts were respectively 12/9 rich immediate, 8/6 compact farm+wood, and
  10/4 compact wood-only.

Artifacts: `field-economy-catalog-calibration-protocol-2026-07-19.md`,
`field-economy-catalog-phase21-local.tsv`, and
`field-economy-catalog-calibration-2026-07-19.json`.

## Frozen selections

| Target archetype | Discovery representative | Discovery macro/full | Confirmation representative macro |
|---|---|---:|---:|
| Rich 3+ farm+wood, immediate TRAIN | `lean_m2c3h0k2` | 1/12, 0/12 | 0/9 |
| Compact farm+wood, deferred TRAIN | `lean_m2c2h0k3` | 4/8, 3/8 | 3/6 |
| Compact wood-only, deferred TRAIN | `dual3_s20_h1_cap12` | 3/10, 2/10 | 0/4 |

The rich family's “winner” is itself evidence of structural failure: a two-worker zero-harvest
chopper was merely least distant, covered only one discovery game, and transferred to none.

## Confirmation gates

| Check | Required | Observed | Pass |
|---|---:|---:|:---:|
| Overall macro uplift | +10 pp | +9/80 = +11.25 pp | yes |
| Overall full uplift | +5 pp | +4/80 = +5.00 pp | yes |
| Catastrophic macro uplift | +15 pp | +1/19 = +5.26 pp | no |
| Worker-rich macro uplift | +15 pp | +1/28 = +3.57 pp | no |
| Every >=4-game target representative >=20% macro | all | rich 0%, compact farm 50%, compact wood 0% | no |
| Exact 160 x 31 grid | exact | 4,960 cells | yes |

The expanded suite moved confirmation macro support from 27/80 to 36/80 and full support from
15/80 to 19/80.  That gain is real but concentrated in ordinary compact games.  Exact-opening
support did not move at all (16/80), and worker-rich full support remained 1/28.

## Multi-level interpretation

- **Parameters:** the GoldElite family has enough range to interpolate a subset of compact
  planting/chopping trajectories.  The discovery-selected cc3/chop3 lean model transferred well
  to compact farm+wood games.
- **Worker design:** every rich configuration still decomposes work into a cheap planter and
  harvest-zero choppers.  Actual rich opponents predominantly buy harvest-capable, chop-capable
  generalists and reach about four productive workers.
- **Role control:** fixed planter/chopper roles cannot reproduce the field's simultaneous high
  harvest, planting, chopping, and banking.  Adding workers changes quantity without supplying
  the dynamic resource-funding coalition that keeps those workers productive.
- **Opening:** none of the selected models adds exact-opening support.  The gap is not repairable
  by grafting only a different TRAIN string because the rich macro trajectory also remains 0/9.
- **Robust-policy implication:** keep the compact representative as descriptive evidence, but do
  not add this catalog wholesale to a minimax suite.  It would add redundant ordinary models
  while leaving the catastrophic/worker-rich uncertainty almost untouched.

## Next experiment

Run the same exact-map, held-out calibration on a small frozen catalog of structurally distinct
existing research controllers: the immediate versatile-worker Boss4 reconstruction, compact
Boss5/BossReal economies, the replay-distilled Norxondor native controllers, and the recovered
Norxondor multi-funder role controllers.  These models change worker stats and dynamic role
allocation rather than retuning GoldElite.

If no member represents the rich immediate family on held-out maps, use the residual feature
errors to write a new purpose-built Legend economy proxy.  Do not reopen direct native imitation
as our candidate; its prior -172.663 margin remains binding.
