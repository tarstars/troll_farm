# LegendFieldProxy v2 — result, 2026-07-19

## Verdict

**Reject v2 and close hand-built universal rich-opponent schedulers.**  Every one of the eight
frozen producer-producer-chopper variants covers 0/12 rich discovery games and 0/9 rich
confirmation games.  The nearest member also fails every material confirmation gate.  Because
no member covers even one rich game, the protocol's coherent-family exception does not apply.

This was consumed-map opponent-model calibration only.  It supplied no candidate, arena game,
submission, or resident change.

## Frozen selection and gates

`legend_v2_balanced_cheap_late_chop` won the predeclared discovery tie-break on normalized
trajectory distance.  The exact audit grid contained 160 x 8 = 1,280 unique cells.

| Gate | Required | Observed | Pass |
|---|---:|---:|:---:|
| Rich confirmation macro | >=20% | 0/9 | no |
| Rich confirmation full | >=1 game | 0/9 | no |
| Overall macro uplift | >=5 pp | +3/80 = +3.75 pp | no |
| Worker-rich macro uplift | >=10 pp | +0/28 | no |
| Catastrophic macro uplift | >=10 pp | +0/19 | no |
| Integrity | 1,280 cells | 1,280 | yes |

The three added ordinary macro/full signatures do not overlap the target rich, worker-rich, or
catastrophic cohorts.  The durable result now records split-specific rich results for every
catalog member and the nearest member for every rich game; all 168 model-by-split macro counts
are zero.

Artifacts: `legend-field-proxy-v2-protocol-2026-07-19.md`,
`legend-field-proxy-v2-phase21-local.tsv`, and
`legend-field-proxy-v2-calibration-2026-07-19.json`.

## What improved—and what did not

The selected v2 proxy reduces rich discovery normalized distance from v1's 1.327 to 1.144.  On
the nine confirmation games it is close at turn 50: mean score error -6.4, worker error +0.11,
plant error +0.11, harvest error -3.2, and chop error -1.2.  At turn 100 mean score error is only
-1.7 and worker error -0.22, although absolute score error has already widened to 35.2.

The continuation then diverges.  Final mean errors are:

- score -260.9;
- wood -62.0;
- workers -0.89;
- plants -10.6;
- harvested fruit -60.3; and
- dropped items -95.3.

Mean chop error (+3.8) is misleading because mean absolute chop error is 75.8: v2 alternately
over- and under-chops while missing the coupled harvest, planting, banking, and workforce path.
Terminal timing is close (4.7 turns mean absolute), so horizon handling does not explain the gap.

## Multilevel conclusion

- **Mechanism:** the replay-level transitions are real, but their ordering and targets are
  state-conditional.  Reproducing transition frequencies is not enough.
- **Controller:** a single deterministic nearest-target grammar enters a different state
  distribution after turn 100 and cannot recover; more fixed role/spec/turn crosses repeat the
  same covariate-shift failure.
- **Population:** the 21 rich games come from heterogeneous named agents.  There is no evidence
  for one universal scheduler, and v2 captures no named subfamily.
- **Research program:** opening and coarse scheduler calibration have reached a plateau.  The next
  model must condition on an observed trajectory or retain per-opponent identity/history.

## Next experiment

Freeze a **replay-conditioned continuation feasibility audit** before building another policy.
For the 21 rich games, use exact official states and command streams to measure at turn 50 and
turn 100 how well nearest-neighbor trajectory retrieval predicts the next 50-turn production
vector under leave-one-game-out and leave-one-opponent-out validation.  Compare map-only,
state-only, and state-plus-action-history retrieval against a split-mean baseline.  Only if
history materially improves held-opponent error may trajectory resampling enter the ambiguity
set; otherwise collect repeated-agent histories and move directly to per-opponent distillation.

