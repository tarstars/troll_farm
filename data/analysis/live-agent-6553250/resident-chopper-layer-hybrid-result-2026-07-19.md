# Resident chopper-layer hybrid — result, 2026-07-19

## Verdict

**Reject and close the complete resident-command swap for the farm's pure chopper. Do not open
seeds 1840--1899.**

The hybrid improves on the low-production resident overall, but it neither preserves the farm's
production nor reproduces the resident's suppression of adaptive Gold. It fails the frozen
worst-opponent and adaptive-margin gates and all four adaptive mechanism gates. Copying selected
resident verbs, adding collision repair, or tuning a switch on seeds 1780--1839 is forbidden.

## Integrity

Two independent integrity runs on seeds 0--29 were byte-identical (SHA-256
`4aae56d9419e93fd7d9ec3357eb09633a694c8a7b22e0acdec8400d32e45e9ff`). All 480 hybrid cells
substituted the pure chopper, the farm shadow had zero command mismatches, crop provenance was
99.96% assigned, and all games completed. The implementation therefore passed its integrity
gate before discovery.

## Discovery result

Fresh seeds 1780--1839 produced 960 common cells across eight opponent families and both seats.

| Frozen check | Result | Required | Pass |
|---|---:|---:|:---:|
| Mean margin versus resident | +22.814 | +10 | yes |
| 5%-trimmed margin versus resident | +27.086 | +5 | yes |
| Own score versus resident | +84.825 | +50 | yes |
| Own wood versus resident | +22.425 | +10 | yes |
| Nonnegative opponent families | 7/8 | 6/8 | yes |
| Worst opponent mean | **-61.667** | -5 | **no** |
| Adaptive-Gold mean | **-61.667** | 0 | **no** |
| Adaptive own score versus farm | **-82.150** | -30 | **no** |
| Adaptive opponent score versus farm | **-37.650** | -50 | **no** |
| Adaptive successful plants versus farm | **-4.033** | -10 | **no** |
| Adaptive self-crop wood versus farm | **-9.433** | -20 | **no** |

Across all opponents, the hybrid loses 58.297 mean margin and 73.511 own score versus the
unchanged farm. On adaptive Gold it loses 44.500 margin versus farm despite lowering the
opponent's score, because the production damage is more than twice the suppression benefit.

## Analysis at different levels

1. **Implementation:** all 960 cells activate and average 144.10 copied turns. The farm shadow
   remains exact, so the result is a real policy-interaction effect rather than wrapper drift.
2. **Command layer:** the resident contribution is not a pure chop-target oracle. It supplies
   79,175 MOVE, 42,486 CHOP, 5,479 DROP, 5,572 PICK, and 5,621 PLANT commands. Its unit action is
   coupled to banking and regeneration decisions made for the complete resident economy.
3. **Private economy:** substituting that action removes 82.15 adaptive-Gold score and 19.31 wood
   from the farm. A productive starter cannot compensate for a chopper whose borrowed schedule
   assumes a different global division of labor.
4. **Reproductive suppression:** opponent planting falls only 4.03 per adaptive game, versus the
   frozen ten-plant mechanism floor and the resident/farm gap of 31.25. Self-crop wood falls only
   9.43. The missing denial is not contained in one worker's target choices.
5. **Coordination:** the resident's advantage is a coherent whole-policy trajectory: global task
   allocation, resource availability, movement conflict handling, and crop creation determine
   which action is useful. A unit-local transplant breaks those dependencies.
6. **Robustness:** seven easy families improve over resident, while the single rich adaptive
   family regresses by 61.67. Mean productivity against weak opponents cannot substitute for the
   opponent-specific robustness needed for a top-three ladder objective.
7. **Transfer:** confirmation, packaging, controlled platform games, and arena submission are not
   authorized. Exact resident submission `41012883`, agent `6560353`, remains active.

## Consequence

Target-layer isolation is disproved, so the conditional pre-fruit target tweak is not eligible.
The next experiment must either preserve coherent whole-policy scheduling or isolate a directly
observed resident failure with a much narrower state invariant. Fresh arena replay evidence now
supplies such a discriminator: rare secure-orchard activations can reserve the starter for more
than 100 apple harvests while a rich opponent compounds. That mechanism receives a
behavior-neutral official-replay audit before any candidate is built.

## Evidence

- `resident-chopper-layer-hybrid-protocol-2026-07-19.md`;
- `resident-chopper-layer-integrity-0-29.tsv` and repeat TSV;
- `resident-chopper-layer-integrity-0-29.json`;
- `resident-chopper-layer-discovery-1780-1839.tsv` and `.json`;
- `rust/src/bin/ownership_aware_complete_economy.rs`;
- `cgauto/resident_chopper_layer_study.py`.
