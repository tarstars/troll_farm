# Opponent-crop harvest-on-contact — result, 2026-07-19

## Verdict

**Close the one-action harvest-on-contact residual without retuning.**

The replay diagnostic found a broad exact-state opportunity, but the complete-policy intervention
is causally harmful.  On all 960 consumed seed/seat/opponent cells, harvest-on-contact loses
**2.325 mean margin** versus exact `b100_e6`; the five-percent-trimmed mean is -1.336.  Only 118
cells improve, 212 worsen, and 630 are unchanged.  The frozen continuation gate fails eight of its
13 checks.

No fresh seed, controlled platform game, candidate artifact, arena submission, or resident change
was made.

## Diagnostic result

All 160 immutable Phase 21 candidate replays parsed successfully.

| Exact-state measure | Result | Frozen gate | Check |
|---|---:|---:|---|
| Eligible crop contacts | 256 | >=80 | pass |
| Games / opponents | 103 / 41 | >=30 / >=12 | pass |
| Immediately collectable fruit | 256 | >=80 | pass |
| Would empty the crop | 141 | >=40 | pass |
| Actual CHOP gained no immediate wood | 244 | >=60 | pass |
| Crops later harvested by opponent | 113 | >=40 | pass |
| Later opponent fruit | 326 | >=60 | pass |
| Catastrophic-game opportunities | 54 | >=25 | pass |

This proves that the normal controller frequently stands on a ripe opponent crop with an empty,
harvest-capable starter and chooses CHOP.  It does not prove that HARVEST is the better action.

## Frozen local prototype

The implementation retains exact provenance and `b100_e6`, executes ordinary target assignment
and movement conflict resolution, then rewrites only the selected `CHOP id` to `HARVEST id` when
the unit currently occupies a ripe tracked opponent crop with empty cargo.  A crop is rewritten at
most once while alive.  A synthetic regression confirms the first eligible chop changes and a
repeated view does not.

Seeds 1300--1359 were already consumed by Phase 17.  Each ran both seats against eight fixed local
opponents.  The 960 cells ran resident, exact `b100_e6`, and the residual from identical initial
states with the corrected stall rule, using 20 workers.

## Complete-policy result

| Incremental measure: harvest minus `b100_e6` | Result | Required | Check |
|---|---:|---:|---|
| Activated cells / opponents | 349 / 8 | >=80 / 8 | pass |
| Harvest rewrites | 612 | >=100 | pass |
| Mean margin delta | **-2.325** | >0 | **fail** |
| 5%-trimmed mean margin delta | **-1.336** | >0 | **fail** |
| Favorable / neutral / unfavorable cells | 118 / 630 / 212 | favorable >= unfavorable | **fail** |
| Mean of 60 per-seed means | **-2.325** | >0 | **fail** |
| Trimmed mean of per-seed means | **-2.052** | >0 | **fail** |
| Mean own-score delta | +0.449 | >=0 | pass |
| Mean own-wood delta | -0.014 | >=0 | **fail** |
| Mean opponent-score delta | **+2.774** | <=0 | **fail** |
| Nonnegative opponents | 1/8 | >=6 | **fail** |
| Worst opponent mean (adaptive Gold) | -7.108 | >=-2 | **fail** |

The effect is not a weak noisy miss.  Among the 349 activated cells, the aggregate deltas imply
about -6.40 margin, +1.24 own score, +7.63 opponent score, and +1.54 opponent wood per activated
cell.  Exact `b100_e6` itself remains +5.517 versus resident on this reused grid; adding harvest
reduces that to +3.192.  The residual destroys about 42% of the parent mechanism's local margin.

## Analysis by level

1. **Action:** the structural candidate-set gap is real, and the rewrite fires 612 times.  Inertness
   does not explain rejection.
2. **Immediate resource:** stealing fruit raises our score slightly, so the command works as
   intended.  It does not preserve wood throughput.
3. **Task sequence:** the carry-1 starter becomes full after one harvest and must bank.  That delays
   the selected fell and interrupts provenance denial.
4. **Shared economy:** the still-standing mature crop remains available to the opponent.  Mean
   opponent wood rises 0.560 per cell, worth about 2.24 score before its additional fruit effects;
   this explains most of the +2.774 opponent-score increase.
5. **Opponent heterogeneity:** seven of eight opponent families lose for us.  Adaptive Gold is
   especially able to exploit the preserved supply (-7.108 margin).  This is not one model's
   artifact.
6. **Experimental method:** an observational opportunity count can establish availability and
   activation breadth, but only closed-loop rollout prices downstream detours and shared assets.
   The two-stage discriminator correctly prevented an arena candidate.
7. **Goal:** a local -2.325 residual cannot advance a rank-3 campaign.  Fruit-count, timing,
   tree-kind, and health filters are prohibited on these consumed results.

## Consequence

- Keep opponent-crop priority as a chop-denial mechanism; do not attach a fruit-harvest prelude.
- Close generic normal-loop harvest-on-contact and the exact one-harvest-per-crop implementation.
- Do not reinterpret the result as evidence against the existing rare idle-harvest endgame branch;
  it acts when ordinary work is absent, whereas this residual displaces selected work.
- Advance the distinct open direction: a bounded representation smoke for a closed-loop,
  outcome-optimized complete economy controller.  The representation must include the resident as
  an exact genotype and co-design workforce, supply, roles, and target policy rather than patch one
  command.

## Evidence

- `opponent-crop-harvest-contact-protocol-2026-07-19.md`;
- `opponent-crop-harvest-contact-diagnostic-2026-07-19.json`;
- `opponent-crop-harvest-contact-local-protocol-2026-07-19.md`;
- `yamo-opponent-crop-harvest-contact-1300-1359.tsv` and `.json`;
- `cgauto/opponent_crop_harvest_contact_diagnostic.py`;
- `cgauto/yamo_crop_harvest_contact_study.py`;
- `rust/src/bin/yamo_crop_harvest_contact.rs`.
