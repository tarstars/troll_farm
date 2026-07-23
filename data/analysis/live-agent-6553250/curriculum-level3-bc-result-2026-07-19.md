# Curriculum Level 3 behavior-clone result — 2026-07-19

## Verdict

Pass.  Transfer from the independently accepted Level-2 checkpoint learns coordinated farmer and
chopper behavior well above every frozen clone threshold.  The prospective PPO controls may be
generated, but this result does not accept Level 3 or authorize a live change.

## Exact evaluation

The deterministic actor was evaluated on the consumed preflight interval, seeds
2,009,000--2,010,999 (2,000 episodes, 240 referee turns).

| Metric | Result | Frozen gate | Margin |
|---|---:|---:|---:|
| Overall success | 1,904/2,000 (95.20%) | 75% | +20.20 pp |
| Nontrivial success | 95.12% | 70% | +25.12 pp |
| Worst height success | 94.01% | 65% | +29.01 pp |
| Tracked crop created | 95.40% | 80% | +15.40 pp |
| Renewable harvest | 96.35% | 70% | +26.35 pp |
| Paired teacher median delay | 0 turns | <=35 | 35 turns |

The four height rates are 95.58% (height 8), 95.99% (9), 95.22% (10), and 94.01% (11).
Successful episodes finish at median referee turn 49, training occurs at median turn 20, and the
median post-training score gain is 16 against the required 12.

## Training observations

The exact run used 600,000 online teacher decisions from stream 6,000,000, seed 71, two shuffled
epochs per 1,000-row chunk, and the frozen cosine learning-rate schedule.  Final-chunk teacher
agreement was 95.10%.  Labels included 102,820 CHOP, 37,419 DROP, 21,934 HARVEST, 7,512 BANANA
PLANT, and 7,526 BANANA PICK decisions, so the fit was not a MOVE-only shortcut.

Wall time was 309.64 seconds and process CPU time was 3,974.35 seconds, corresponding to 64.18% of
the 20-logical-CPU host.  Evaluation produced 240,700 actor decisions at 11,185 decisions/s.

## Pre-PPO role-audit baseline

The subsequently frozen strict audit gives the clone 88.42% exact productive-command agreement
for the chopper and 55.39% for the farmer.  Farmer verb agreement is already 91.25%, so its 4.61-
point shortfall from the final PPO action gate is spatial target precision rather than missing
PICK/PLANT/HARVEST/DROP behavior.  It emits 11,273 combined unjustified selected-unit waits, below
the 20,000 ceiling.  This is diagnostic only: the action gate applies to final PPO, not the clone.

Audit hash: `db236e2fbdb74d87d997bece64bd2a9b1b88cceafce19ac06f70d1af364982d6`.

## Reproducibility anchors

- initialized Level-2 checkpoint:
  `8a831f6f7878eef898af4377530c291e577cc58750860c20c89a9005a5e19926`;
- Level-3 clone checkpoint:
  `6ea48c4e65d8bb5d786e8b47966bc60bcdd8684cc9de9e580e4e3de5ca2a2a8d`;
- exact evaluation:
  `3545004de67d87e6ac0ff5bcd1fa7a4a4e39479047b506f3f2593be978684c47`;
- training summary:
  `24e68e54d9b69cc777f202a6f47089c9e6e30617d0d2a20cf832b35866938d11`;
- frozen protocol:
  `b43a586e2e8593b5044a219271721ece9c9d273f7cbf4d2b63d7cd86e59f896d`.

## Next eligible experiment

Generate and hash the teacher/random controls for exact prospective seeds
2,011,000--2,012,999, preflight the Level-3 PPO path on development-only streams, then run the
unchanged four-million-decision discovery from this exact clone checkpoint.  Stage A remains at
one million decisions and is a hard stop if any renewable milestone gate fails.
