# Total Map Value Ownership Diagnostic Report

Decision: **PROCEED: build v1.53.0-pressurefarm**.

The repeatable signal is not "created farm value only." It is broader: losses repeatedly show
large **own-half exposed** value by t150, with most remaining map value projected as opponent-owned
or contested before the opponent's late wood burst. Created farm exposure appears in several losses,
but it is smaller than the own-half exposure signal.

## Corpus

Fresh `@TFOWN` DEBUG games collected after the Rust diagnostic was added:

| Group | Opponent | Games | Result |
|---|---:|---:|---:|
| Field | 6480966 / plcc | 895549831, 895549851 | 0-2 |
| Field | 6480914 / mikdiet | 895549876, 895549889 | 1-1 |
| Field | 6480824 / kurigen | 895549908, 895549929 | 0-2 |
| Context | boss | 895549961, 895549976, 895549991, 895550010 | 0-4 |

Old raw games were used only to confirm the telemetry gap: they contain map, initial tree rows,
per-turn inventories/positions, and summaries, but not per-turn tree coordinates. Exact ownership
verdicts therefore come from the fresh `@TFOWN` corpus.

CSV artifacts:

- `data/analysis/map-value-ownership/tfown_field_rows.csv`
- `data/analysis/map-value-ownership/tfown_boss_rows.csv`
- `data/analysis/map-value-ownership/tfown_rows.csv`

## Model Constants

From `@TFOWNCFG`:

| Constant | Value |
|---|---:|
| ETA bucket margin | 3 turns |
| future seed addend | 1 |
| created near-tent radius | 2 |
| farm radius | 2 |

The model scores live trees as `4 * size + fruits + future_seed_addend` for ripe banana/apple
seed sources. Ownership is a rough ETA race from live workers to tree/action/bank. This is a loss
classifier, not a direct policy.

## Field Averages

Primary verdict uses the 6 field games only.

| t | games | total | ours | opp | uncertain | dead | created_exposed | own_half_exposed |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 75 | 6 | 347.8 | 77.3 | 220.2 | 50.3 | 0.0 | 0.0 | 52.0 |
| 150 | 6 | 369.7 | 38.0 | 264.0 | 67.7 | 0.0 | 7.3 | 78.8 |
| 225 | 6 | 226.2 | 24.3 | 184.8 | 17.0 | 0.0 | 0.0 | 43.2 |
| 300 | 6 | 105.7 | 0.0 | 0.0 | 0.0 | 105.7 | 0.0 | 37.5 |

Field loss split:

| t | losses | total | ours | opp | uncertain | created_exposed | own_half_exposed |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 75 | 5 | 331.0 | 60.2 | 218.2 | 52.6 | 0.0 | 62.4 |
| 150 | 5 | 385.2 | 45.6 | 266.0 | 73.6 | 8.8 | 79.0 |
| 225 | 5 | 240.6 | 21.4 | 198.8 | 20.4 | 0.0 | 51.8 |
| 300 | 5 | 111.2 | 0.0 | 0.0 | 0.0 | 0.0 | 41.0 |

The one field win still had a high t150 opponent bucket, so the model is not a standalone win
predictor. The stronger loss discriminator is persistence of own-half exposed value into t150/t225
plus the later opponent wood burst.

## Boss Context

Boss context also shows the same broad shape, though it is not the primary verdict corpus:

| t | games | total | ours | opp | uncertain | dead | created_exposed | own_half_exposed |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 75 | 4 | 345.5 | 58.8 | 158.2 | 128.5 | 0.0 | 5.0 | 64.0 |
| 150 | 4 | 321.0 | 50.2 | 175.5 | 95.2 | 0.0 | 3.0 | 46.8 |
| 225 | 4 | 289.8 | 29.5 | 171.8 | 88.5 | 0.0 | 1.0 | 54.5 |
| 300 | 4 | 255.2 | 0.0 | 0.0 | 0.0 | 255.2 | 0.0 | 71.5 |

## Top Exposures

Top `created_exposed` at t150/t225:

| value | game | opp | result | t | total | ours | opp | uncertain |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 20 | 895549851 | 6480966 | L | 150 | 571 | 92 | 381 | 98 |
| 16 | 895549908 | 6480824 | L | 150 | 170 | 32 | 103 | 35 |
| 8 | 895549929 | 6480824 | L | 150 | 240 | 0 | 194 | 46 |
| 8 | 895549991 | boss | L | 150 | 311 | 80 | 139 | 92 |
| 4 | 895549961 | boss | L | 150 | 365 | 77 | 201 | 87 |

Top `own_half_exposed` at t150/t225:

| value | game | opp | result | t | total | ours | opp | uncertain |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 118 | 895549876 | 6480914 | L | 150 | 333 | 16 | 203 | 114 |
| 104 | 895549929 | 6480824 | L | 150 | 240 | 0 | 194 | 46 |
| 99 | 895549876 | 6480914 | L | 225 | 268 | 0 | 209 | 59 |
| 98 | 895549851 | 6480966 | L | 150 | 571 | 92 | 381 | 98 |
| 96 | 895550010 | boss | L | 225 | 211 | 20 | 51 | 140 |

## Replay Narrative

Game 895549851 vs plcc is the cleanest pressure-farm example.

At t150 the bot is ahead on score and wood: score 182-24, wood 42-4, with 31 trees still on the
map. The ownership model already says the remaining tree value is mostly not safe for us:
`total=571 ours=92 opp=381 uncertain=98 created_exposed=20 own_half_exposed=98`.

By t225 the score has nearly collapsed to 270-269 and opponent wood has jumped from 4 at t150 to
65. The ownership row has also collapsed: `total=167 ours=23 opp=101 uncertain=43
own_half_exposed=43`. By t300 the final is a loss, 322-403, with wood 78-100.

This is the ownership leak the plan was looking for: value existed on/near our side before the
late burst, was not safely ours, and the opponent converted enough of it to flip the game.

## Candidate Brief

Build `v1.53.0-pressurefarm`, but keep it narrow and observed-triggered.

First priority: use the ownership score in decision making and measure the behavioral influence.
Do not spend the next step on AUROC/model-validation work.

Allowed behavior changes:

- dynamic farm cap under observed pressure;
- seed-reserve release under observed pressure;
- exposed farm tree liquidation;
- optional own-half pressure trigger that only raises urgency for already local/exposed value;
- no global planner rewrite.

Do not implement:

- always smaller farm;
- always earlier liquidation;
- static turn-gated roam widening;
- simple seed-home priority;
- global total-map planner.

The first candidate should key off the measured pattern: by t150/t225, if nearby/own-half value is
projected opponent-owned or uncertain and our local farm contains exposed created value, stop
expanding and convert/liquidate local value before the opponent's ETA window.

## Postponed Target

AUROC-style supervised validation is useful but postponed. The current corpus has only one win, so
AUROC mostly measures whether losses rank above that single win. Revisit this after behavior work
creates a larger, more balanced corpus. Target shape for later:

- target: loss = 1, win = 0;
- scores: `own_half_exposed`, `created_exposed`, `opp_share`, `not_ours_share`, composite pressure;
- minimum useful corpus: roughly 20 wins and 20 losses per major opponent class;
- output: AUROC by phase plus confidence notes.

## Verification

- `cargo test --release --test map_value_ownership`: 2 passed.
- `cargo test --release`: passed.
- Bundle compile: passed.
- Minified compile: passed.
- Minified size: 66,994 bytes.
- `DEBUG=true` smoke test emitted `@TFOWNCFG` and `@TFOWN`.
- Bundled equality vs release bot: `EQUAL: 32 games`.
- Minified equality vs release bot: `EQUAL: 32 games`.
