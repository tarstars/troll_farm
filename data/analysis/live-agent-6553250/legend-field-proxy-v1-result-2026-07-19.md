# LegendFieldProxy v1 — result, 2026-07-19

## Verdict

**Reject the fixed v1 grammar.**  All eight variants cover 0/12 rich discovery games; the
least-distant unchanged representative then covers 0/9 rich confirmation games and adds no new
overall, catastrophic, or worker-rich support to the old zoo.  More farmer-count, fell-start, or
the two consumed ladder variants is not justified.

This was opponent-model work only.  No candidate or resident conclusion follows from its score,
and the arena was untouched.

## Frozen selection and gates

`legend_balanced_f2_fell100` was selected by lowest discovery distance after all variants tied at
zero macro and full coverage.  The exact grid contained 160 x 8 = 1,280 trajectories.

| Gate | Required | Observed | Pass |
|---|---:|---:|:---:|
| Rich confirmation macro | >=20% | 0/9 | no |
| Rich confirmation full | >=1 game | 0/9 | no |
| Overall macro uplift | >=5 pp | +0/80 | no |
| Worker-rich macro uplift | >=10 pp | +0/28 | no |
| Catastrophic macro uplift | >=10 pp | +0/19 | no |
| Integrity | 1,280 cells | 1,280 | yes |

Artifacts: `legend-field-proxy-v1-protocol-2026-07-19.md`,
`legend-field-proxy-v1-phase21-local.tsv`, and
`legend-field-proxy-v1-calibration-2026-07-19.json`.

## Residual shape

The selected v1 proxy is close at turn 50 in score (+0.8), wood (-1.4), workers (-0.1), harvest
(-3.6), and chops (-2.2), though it already under-plants by 7.1.  At turn 100 it remains within
one worker but is behind by 13 score, 6 plants, 13 harvested fruit, 7 chops, and 20 dropped items.

By final it is behind by:

- 328.6 score;
- 83.3 wood;
- 1.22 workers;
- 31.2 plants;
- 65.4 harvested fruit; and
- 145 dropped items.

It actually issues 21.7 more successful chop actions on average, but mean absolute chop error is
92.1.  This is not a simple “chop more” deficit: the scheduler burns or contests supply
inconsistently while failing to fund, harvest, plant, and bank at field scale.

## Conclusion at several abstraction levels

- **Training:** a plausible immediate first spec is insufficient; the later workforce still
  averages 1.22 workers below the field.
- **Task allocation:** static ordinal farmers plus deterministic nearest targets do not create the
  observed renewable loop.
- **Production:** the missing mass is mostly after turn 100 and spans every productive channel,
  indicating a coupled scheduler rather than one action threshold.
- **Modeling:** outcome fitting on nine rich confirmation maps would overfit the same consumed
  trajectories.  The next information source must be their action transitions, not another
  terminal-parameter grid.

## Next experiment

Decode the exact 21 rich-immediate arena trajectories and split them by the existing SHA rule.
Measure successful later TRAIN specs/timing, funding contributors, per-worker phase actions,
multi-role behavior, action transitions, and 50-turn production increments.  Only mechanisms
that repeat on both 12-game discovery and 9-game confirmation may enter v2.
