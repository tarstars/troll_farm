# Structural field-proxy calibration — frozen protocol, 2026-07-19

## Question

Do existing structurally distinct research controllers reproduce the three Legend economy
archetypes that the old zoo and all 31 fixed GoldElite configurations miss, especially immediate
worker-rich farm+wood opponents?

This is opponent-model reconstruction only.  Several controllers below are known to lose badly
when used as our complete policy; that evidence remains binding and is not retested here.

## Frozen controller catalog

Run exactly these eleven default, unchanged controllers:

1. `boss4` — immediate harvest/chop-capable versatile workers, up to four;
2. `boss5` — compact immediate printer/chopper economy;
3. `boss_real` — compact renewable pure-harvest farm;
4. `norx_native_full` — replay-distilled staged workforce, intents, persistent goals, and dynamic
   harvest/chop/farm/mine roles;
5. `norx_native_three` — the same native controller capped after worker three;
6. `norx_compact` — recovered staged generalist ladder over CompactGold;
7. `norx_silver` — recovered staged generalist ladder over SilverBoss;
8. `norx_funded_silver` — one explicit funding role;
9. `norx_cooperative_silver` — two coordinated funders through the full ladder;
10. `norx_soft_cooperative_silver` — two funders until worker three, then one; and
11. `norx_three_worker_silver` — two funders until worker three, then stop training.

Do not add Rhea: its wall-clock anytime loop makes this a runtime comparison rather than a fixed
deterministic continuation.  Do not alter TRAIN bases/caps, funding schedules, intent trees,
rankers, or continuation parameters after observing results.

## Inputs, split, scoring, and selection

Use the same 160 exact normalized maps, exact `b100_e6` player-0 policy, referee/event counters,
old-zoo baseline union, frozen tolerances, and SHA-256 discovery/confirmation assignment from
`field-economy-catalog-calibration-protocol-2026-07-19.md`.

Run 160 x 11 = 1,760 complete trajectories using 20 workers.  For each of the same three target
archetypes, select on discovery the single controller with more macro-covered games, then more
fully covered games, then lower mean normalized macro distance, then lexicographic label.
Deduplicate winners before confirmation.

### Pre-outcome terminal-state amendment

The first analyzer attempt stopped on its integrity check before producing any selection or gate
outcome: `norx_funded_silver` reached the referee's terminal/stall condition at turn 98 in game
`896284387`, so the runner encoded its turn-100 snapshot as missing.  A game that has terminated
has an absorbing final state, not an unknown state.  Before rerunning or reading any catalog
ranking, freeze this rule for all models and maps: if a local game terminates before turn 50 or
100, carry its exact terminal state and cumulative counters forward to the missing checkpoint,
while retaining the true terminal turn for the independent terminal-error comparison.  Do not
drop the cell, extend play past the referee terminal, or relax any tolerance.

## Frozen confirmation gates

Use the same material-representation gates as the preceding catalog smoke:

1. exact, unique 160 x 11 grid with every checkpoint, including the frozen absorbing-terminal
   encoding above;
2. old zoo plus selected representatives improves overall macro support by >=10 percentage
   points on confirmation;
3. overall full support improves by >=5 percentage points;
4. catastrophic macro support improves by >=15 percentage points;
5. worker-rich macro support improves by >=15 percentage points; and
6. each target archetype with at least four confirmation games is macro-covered by its own
   discovery representative at >=20%.

Also report exact-opening change and per-feature/checkpoint residuals for the selected rich model.

## Stop and continuation rules

- **All gates pass:** retain only the selected controllers as opponent proxies and rerun the
  global coverage gate before any policy optimization.
- **Macro gates pass but full support fails:** isolate whether opening mismatch explains the loss
  and freeze a separate opening graft if warranted.
- **Rich or critical macro gates fail:** close reuse of existing controllers.  Build one new
  purpose-specific Legend proxy from the rich representative's held-out residuals, using
  harvest-capable generalists and dynamic funding/production roles.  Do not tune these eleven on
  either partition.

No fresh seed, arena write, candidate, submission, or resident change is authorized.
