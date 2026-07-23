# Curriculum Level 4 independent confirmation PPO Stage A — 2026-07-19

## Verdict

Pass. At exactly one million decisions, the independently initialized seed-89 actor clears every
frozen Stage-A safety gate on exact seeds 2,017,000--2,018,999. The same process continues
unchanged to four million decisions. This intermediate result does not accept Level 4 or authorize
a live submission.

| Metric | Stage-A result | Frozen floor | Margin |
|---|---:|---:|---:|
| Overall success | 1,968/2,000 (98.40%) | 60% | +38.40 pp |
| Nontrivial success | 97.95% | 55% | +42.95 pp |
| Worst recipe success | 96.01% | 45% | +51.01 pp |
| Worst height success | 97.80% | 50% | +47.80 pp |
| Tracked crop created | 98.55% | 65% | +33.55 pp |
| Renewable harvest | 98.65% | 55% | +43.65 pp |
| Paired teacher median delay | 0 turns | <=55 turns | 55 turns |

The weakest recipe is hybrid chopper at 96.01%; harvest producer is 96.33%, and the other six
families are at least 98.06%. Height buckets range from 97.80% to 99.40%. Median
training/completion turns are 14/52 and median post-training score gain is 15.

The pre-registered process continued automatically after the passing evaluation. No checkpoint
was selected, no parameter changed, and no training/evaluation seed was inspected for tuning.

## Reproducibility anchors

- Stage-A checkpoint:
  `62c7030a319375fcb4c2df6964908bbccfe4afbea592cbe439f4eeb13f8329c0`;
- exact Stage-A evaluation:
  `86df57cae954aa5ab20379fcd8b54153894fc7a3411794fb6fd0b7c44c4395cc`;
- frozen protocol:
  `ea4c66a270effb9040db17b2476e61bcf88f1edf2719051f6ffea42571022596`;
- independent transfer clone:
  `a5aab5d22a667268316ab620767964f2f9a088af9e545a14f7993511a4780ead`.

## Continuation

Continue the exact seed-89 optimizer and stream to four million decisions. Decide confirmation
only from the final functional evaluation and the separately executed strict recipe-by-role action
audit.
