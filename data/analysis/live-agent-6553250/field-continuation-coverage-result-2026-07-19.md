# Full-trajectory field-continuation coverage audit — result, 2026-07-19

## Verdict

**The fixed eight-model continuation zoo fails the frozen field-support gate.**  It must not be
used as a calibrated ambiguity set, rollout-weight source, or candidate acceptance oracle.  In
particular, adaptive Gold is not a material proxy for the worker-rich or catastrophic Legend
cohorts.  Its large veto against the complete-economy smoke remains a real local counterexample,
but it is not direct evidence that the same regression is common in the field.

This was a diagnosis-only experiment.  It authorizes no candidate, fresh qualification data,
controlled arena game, submission, or resident change.

## Integrity and artifacts

- Cohort: all 160 consumed Phase 21 candidate games for agent `6560269`.
- Normalization: exact formatted `b100_e6` as local player 0 on every official initial state.
- Map dataset SHA-256: `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.
- Local grid: 160 maps x eight frozen models = 1,280 complete trajectories.
- Runner: 20 workers, corrected terminal/stall rule, no missing turn-50/turn-100/final snapshot.
- Frozen protocol: `field-continuation-coverage-protocol-2026-07-19.md`.
- Observed signatures: `field-continuation-phase21-candidate-160-observed.json`.
- Local trajectories: `field-continuation-phase21-local.tsv`.
- Full scored matrix: `field-continuation-coverage-2026-07-19.json`.

All integrity checks passed.  The only execution defect was a direct-script Python import path;
it failed before loading the result data, was fixed, and the frozen scorer's tests then passed.

## Frozen gate result

| Cohort/check | Required | Observed | Pass |
|---|---:|---:|:---:|
| Overall full coverage | >=70% | 31/160 = 19.38% | no |
| Catastrophic full coverage | >=70% | 2/31 = 6.45% | no |
| Worker-rich full coverage | >=60% | 1/51 = 1.96% | no |
| Exact opening support | >=50% | 30/160 = 18.75% | no |
| Every >=5-game opponent >=50% | 50% | 6/11 sampled opponents below 20%; five at 0% | no |
| Complete 160 x 8 grid | exact | 160 x 8 | yes |

Opening mismatch is not the only problem.  Some current model macro-trajectory covered only
52/160 games even before requiring the coarse opening; only 31 remained after the opening gate.
Every existing model shares the same coarse-opening support count (69), which shows that the zoo
has many nominally different implementations but little first-turn policy diversity.

## Adaptive-Gold diagnostic

Adaptive Gold was nearest by normalized macro distance on 8/31 catastrophic games (25.81%) and
13/51 worker-rich games (25.49%), so it detects a broad direction that the weaker models miss.
However, it macro-covered **0/31 catastrophic** and **0/51 worker-rich** games under the frozen
tolerances.  It therefore failed two of four relevance checks and the material-field-proxy gate.

This resolves the apparent contradiction in the preceding complete-economy smoke: the farm
grammar's `-47.933` result against adaptive Gold proves vulnerability to that synthetic shared-
supply policy, but the local model is too far from actual strong-opponent production trajectories
to set a field-wide worst-case floor.

## Missing field archetypes

The three largest coherent uncovered clusters are:

1. **Immediate rich farm+wood:** 21 games, mean 3.95 workers, 52 successful plants, 113.4 chops,
   95.2 wood, and 420.5 score.  These opponents train immediately; the dominant first specs are
   `2/2/2/1` (7) and `2/2/1/1` (5), not the zoo's narrow chopper template.
2. **Deferred compact farm+wood:** 14 games, exactly two workers, 30.6 plants, 101.4 chops, 46.1
   wood, and 209.1 score.  They do not TRAIN on turn one and combine renewable planting with high
   chopping throughput.
3. **Deferred compact wood-only:** 14 games, exactly two workers, 11.8 plants, 108.4 chops, 32.7
   wood, and 140.1 score.  They also defer TRAIN, but invest much less in renewable farming.

The rich archetype spans 14 different opponent names.  It is a league-level policy family, not
an idiosyncratic replay from one bot.  Conversely, adding more labels around the existing default
Gold implementation cannot fix the gap: CompactGold and default GoldElite produced identical
coverage and distance summaries.

## Analysis at different abstraction levels

- **Command level:** exact TRAIN/starter support is only 18.75%; the model suite omits the field's
  common harvest-capable immediate worker specifications and several deferred openings.
- **Role/economy level:** the largest missing family sustains roughly four workers while both
  planting and chopping heavily.  Existing adaptive Gold is directionally close but materially
  under- or over-shoots too many checkpoints to cover a single critical game.
- **Interaction level:** the actual strong economies coexist with `b100_e6` on the exact maps.
  Their observed output cannot be dismissed solely as the shared-supply runaway produced by the
  synthetic adaptive model.
- **Model-selection level:** robust minima and opponent weights from the old zoo are uncalibrated;
  they can reject productive policies for the wrong continuation and favor policies against
  redundant weak models.
- **Arena level:** this audit does not prove that the closed farm candidate would transfer.  It
  removes an invalid negative inference and identifies what must be represented before reopening
  terminal-outcome optimization.

## Next experiment

Run a frozen, exact-map calibration smoke over the already-defined 31 complete-economy configs.
For each config, play exact `b100_e6` against it on all 160 consumed maps and score the same
opening/macro signatures without changing tolerances.  Measure the incremental union coverage
over the old zoo and use weighted set cover to nominate, at most, one representative for each of
the three missing archetypes.

This is representation reconstruction, not candidate tuning: it consumes no new seeds or arena
games and cannot qualify a policy.  If the existing catalog cannot materially lift critical-
cohort coverage, close parameter tuning of GoldElite and move to a structurally new field-proxy
controller with harvest-capable workers and replay-derived role allocation.
