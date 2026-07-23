# Ownership-aware complete economy — result, 2026-07-19

## Verdict

**Reject and close the exact race-conditioned rate controller. Do not open seeds 1720--1779.**

The controller preserves the productive private farm and improves it by +5.883 mean margin, but
it does not suppress adaptive Gold deeply enough to recover the resident's denial advantage. It
fails three frozen discovery checks: worst-opponent margin, adaptive-Gold margin, and adaptive
opponent-score suppression. No rate, size, race, worker, or activation threshold may be tuned on
the consumed 1660--1719 block.

## Integrity and deterministic infrastructure repair

Before opening fresh data, unordered equal-cost target choices in four sparring controllers and
unordered simultaneous plant insertion were made canonical. Two independent 0--29 integrity runs
then produced byte-identical 1,440-row TSVs with SHA-256
`caff9bb2d2a293540356acc520d71416bbdf2dfc455e0b55c7f7dd0e7a2a8fa4`.

All 480 scenario grids completed, the wrapper's internal farm shadow reported zero command
mismatches, and provenance assigned 99.966% of chopped wood. This repair changed no controller
formula or acceptance threshold and was completed before seeds 1660+ were opened.

## Frozen discovery result

The run contains 60 seeds, both seats, eight opponents, and three common profiles: 960 cells per
profile. Ownership-aware versus exact resident clears the broad productivity checks:

| Measure | Result | Frozen floor | Pass |
|---|---:|---:|:---:|
| Mean margin delta | +72.074 | +10 | yes |
| 5%-trimmed margin delta | +76.398 | +5 | yes |
| Own-score delta | +163.131 | +50 | yes |
| Own inventory-wood delta | +38.993 | +10 | yes |
| Nonnegative opponent families | 7/8 | 6/8 | yes |
| Worst opponent mean | **-46.925** | -5 | **no** |
| Adaptive-Gold mean | **-46.925** | 0 | **no** |
| Activated cells | 406/960 | 200 | yes |
| Adaptive activated cells | 64/120 | 30 | yes |

Against the unchanged farm, the override is directionally useful: own score changes only +0.229,
opponent score falls 5.654, and margin rises 5.883. On adaptive Gold specifically it preserves
own score within -2.258 and lowers opponent score 15.967, for +13.708 margin. The frozen mechanism
gate required at least 25 points of opponent-score suppression, so it fails there too.

## Analysis at different levels

1. **Implementation:** inactive cells are exactly identical to the farm across every recorded
   outcome and provenance field. Effects are caused by the override, not wrapper drift.
2. **Command mechanism:** 406/960 cells activate, with median first activation at turn 60. The
   active-cell margin effect is +13.911 versus farm; on adaptive Gold it is +25.703. Inactivity is
   not the sole problem: even extrapolating the observed active effect does not cover adaptive
   Gold's 60.633-point resident advantage over farm.
3. **Resource allocation:** the controller preserves private production. It trades only 0.022 own
   wood/game versus farm while taking 3.138 more wood from opponent crops and reducing rival
   self-crop wood by 1.768.
4. **Reproductive loop:** this is the decisive abstraction. Against adaptive Gold it reduces
   opponent successful plants by only 1.558/game, while resident prevents 31.250 of the farm
   profile's excess plantings. It reduces rival self-crop wood by 6.167/game but recovers only
   22.61% of the resident/farm margin gap. Pricing mature wood cycles liquidates output after the
   compounding chain is already established.
5. **Opponent interaction:** seven families remain strongly above resident. Adaptive Gold is the
   unique robustness counter; SilverBoss also shows a -2.725 regression versus farm, with -8.385
   conditional on activation, proving that a locally rational current-cycle comparison is not a
   universally correct game-level objective.
6. **Complete-game/tail:** mean and trimmed results are strong, but individual deltas reach -320
   versus resident and -178 versus farm. The rank-3 objective cannot accept that concentrated
   opponent and tail risk.
7. **Transfer:** the controller is not eligible for confirmation, packaging, field-prefix audit,
   platform games, or arena submission. The exact resident remains live.

## Attack-angle matrix after closure

| Priority | Attack angle | New information it targets | Main risk | Next discriminator |
|---:|---|---|---|---|
| 1 | Resident chopper-layer component swap | Whether resident target scheduling, rather than its whole economy, causes the 31-plant suppression gap | Cross-controller coordination | Farm starter/economy plus exact resident command for the pure chopper |
| 2 | Pre-fruit reproduction interruption | Kill a crop before it yields the seed that creates the next crop | Long denial travel; resembles a rejected crop chase if not race-bounded | First-fruit and enemy-harvest race controller, only if layer swap proves target-policy value |
| 3 | Observable regime selector | Preserve resident against self-compounding opponents and farm against passive ones | Early classification and path dependence | Shadow-policy upper bound followed by held-family behavioral classification |
| 4 | Passively funded third denial worker | Remove the one-chopper opportunity-cost conflict | Training can collapse the farm; generic three-worker genomes already failed | Only after a scheduler preserves the two-worker farm cycle while funding |
| 5 | Joint task assignment | Coordinate private production, banking, and denial globally | Larger representation and distillation cost | Small exact assignment layer with shuffle-invariance tests |
| 6 | Late macro search/distillation | Choose regime from induced trajectory rather than a fixed rule | Prior online search exceeded 50 ms and compact learners did not transfer | Reopen only with a calibrated opponent model and deployable runtime bound |

The resident-chopper component swap is first because it is coefficient-free, isolates one causal
layer, reuses the only policy known to create the missing reproductive suppression, and is cheaper
and more informative than immediately adding another worker or fitted compounding value.

## Evidence

- `ownership-aware-complete-economy-protocol-2026-07-19.md`;
- `ownership-aware-complete-economy-integrity-0-29.tsv` and repeat TSV;
- `ownership-aware-complete-economy-integrity-0-29.json`;
- `ownership-aware-complete-economy-discovery-1660-1719.tsv` and `.json`;
- `rust/src/strategies/ownership_aware_farm.rs`;
- `rust/src/bin/ownership_aware_complete_economy.rs`;
- `cgauto/ownership_aware_complete_economy.py`.
