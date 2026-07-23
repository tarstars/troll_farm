# Renewable-supply study

## Baseline supply cliff

Exact live self-play over 60 maps (120 side-games, eight workers) confirms a real supply cliff:

| turn | mean shared trees | mean ripe trees |
|---:|---:|---:|
| 1 | 16.23 | 6.87 |
| 50 | 4.82 | 4.28 |
| 100 | 1.55 | 0.22 |
| 150 | 0.48 | 0.15 |
| 200 | 0.18 | 0.13 |
| 250 | 0.20 | 0.13 |
| 300 | 0.03 | 0.00 |

The first empty-board state occurs in 116/120 side-games, at median turn 81.5. At first
exhaustion, 86 sides still have banked fruit and 69 have banana. The live bot already converts
that stock aggressively: it averages 12.89 plants, with median last plant at turn 113.5. Only
18/120 sides plant after turn 150. The apparent late-harvest mean is entirely two secure-orchard
outliers with 75 harvests each.

Thus two separate mechanisms must not be conflated:

1. stored-fruit scheduling, which live already performs near exhaustion;
2. true renewal, which must harvest a standing mother and risks giving its mature wood to the
   opponent.

The original timeline forced all games to turn 300.  Under the corrected referee semantics,
116/120 side-games (58/60 matches) terminate by stall at median turn 129.  The live bot issues
200 plant commands inside no-tree grace windows and successfully replants an empty board 148
times across 45/60 matches.  Renewal during grace is therefore normal live behavior, not a
missing capability.

Raw timelines:

- original fixed horizon: `data/analysis/live-agent-6553250/renewable-supply-baseline.json`;
- corrected stall semantics:
  `data/analysis/live-agent-6553250/renewable-supply-stall-corrected-2026-07-16.json`.

## Candidate sequence

All results are paired local self-harm checks on the same 60 seeds unless marked otherwise. They
are not arena predictions.

| candidate | mechanism | n | margin | wood | W/T/L | plant delta | harvest delta |
|---|---|---:|---:|---:|---:|---:|---:|
| late supply loop | mother/crop at t>=100 and <=2 trees | 60 | -11.77 | -2.89 | 11/9/40 | +1.70 | +1.56 |
| exhausted loop | start only at zero trees | 60 | -6.13 | -1.53 | 4/28/28 | +0.61 | +0.63 |
| supply pulse | release mother after first crop | 60 | -6.50 | -1.63 | 3/27/30 | +0.66 | +0.68 |
| banana pulse | reject slower mother kinds | 60 | -1.77 | -0.44 | 6/39/15 | +0.17 | +0.18 |
| mother-first pulse | liquidate ripe mother before crop | 60 | -1.27 | -0.32 | 6/40/14 | +0.18 | +0.18 |
| overlap-one pulse | start with one ordinary tree left | 60 | -1.40 | -0.38 | 11/28/21 | +0.12 | +0.23 |
| low-supply pre-seed, old fixed-300 result | shift existing PICK/PLANT earlier | 200 | +0.06 | +0.02 | 21/158/21 | 0.00 | 0.00 |
| low-supply pre-seed, corrected stall result | seed before terminal supply collapse | 1,000 | **+0.259** | **+0.115** | **221/655/124** | +0.246 | +0.008 |

The first loop creates supply but displaces 14.48 chops and adds 22.43 moves per game. Tightening
activation and releasing the mother reduce, but never reverse, the wood loss. The best true
renewal pulse still loses 0.32 wood and has more than twice as many losing as winning seeds.
Moving the pulse earlier to avoid stall termination raises travel/chop disruption again.

The old timing-only conclusion was an evaluator artifact.  With the real early-end rule, the
pre-seed branch has time to prevent or exploit a terminal supply collapse: at 1,000 paired seeds
it adds 0.209 PICKs and 0.246 PLANTs, loses only 0.069 CHOPs, and gains 0.115 banked wood per map.
Its +0.259 paired margin has standard error 0.0623 and a normal-approximation 95% interval of
[+0.137, +0.381].

## Verdict

The true-renewal loops remain rejected, but low-supply pre-seeding now **qualifies for controlled
field evidence**.  It also passes a 200-game inactive-region equality check through turn 99 and
activates on 14/19 admissible baseline-reproducing historical streams, always at an eligible
state.  There were zero platform games and zero arena submissions; exact live agent `6553250`
remains unchanged.

The structural constraint is now explicit: with a chop-1/carry-1/harvest-1 starter and a trained
worker that normally has harvest 0, producing a new seed requires a harvest/plant cadence whose
action cost and exposed mature mother exceed the resulting private wood. A future renewable
design must make supply exclusive—through geometry or a worker that can harvest without reducing
fell capacity—not merely create more shared trees.

The pre-seed result does not overturn that constraint: it schedules already banked fruit before
the referee closes the game; it does not make a standing mother privately profitable.
