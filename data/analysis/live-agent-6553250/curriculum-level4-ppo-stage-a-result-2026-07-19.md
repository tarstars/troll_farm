# Curriculum Level 4 PPO Stage-A result — 2026-07-19

## Verdict

Pass.  At exactly one million decisions, the seed-83 PPO actor clears every frozen Stage-A gate on
the complete 2,000-map discovery bank.  The same process continues unchanged to four million
decisions; this intermediate read does not accept Level 4 or authorize submission.

| Metric | Observed | Frozen Stage-A floor |
|---|---:|---:|
| Overall success | 1,986/2,000 (99.30%) | 60% |
| Nontrivial success | 99.21% | 55% |
| Worst recipe success | 98.43% | 45% |
| Worst height success | 98.80% | 50% |
| Tracked crop created | 99.40% | 65% |
| Renewable harvest | 99.55% | 55% |
| Paired teacher median delay | 0 turns | <=55 turns |

The eight recipe success rates range from 98.43% (cheap planter) to 100% (compact farmer and
balanced producer).  Median training/completion turns are 12/52 and median score gain is 15.
Relative to the passing clone, PPO improves overall success by 1.50 points and the recipe floor by
5.10 points while retaining zero aggregate teacher delay.

The stochastic rollout trace briefly explored down to 97.9% recent success near 300,000 decisions,
then recovered above 99% before Stage A.  KL remained controlled by the frozen early-stop rule;
undefined auxiliary targets were rare and skipped exactly as prescribed.

## Anchors and continuation

- Stage-A checkpoint:
  `689206aecf396707670f9205cd68bfc76539d74912916363e2a012a8a78d7cce`;
- exact Stage-A evaluation:
  `1019229a4461c6db379adc4b0c96a1cba7205a246ff929e9b86712505a7897eb`;
- recipe-by-role audit implementation:
  `305ff6f59582aa1eef46d632d7482b4cbec789e3f13655dd0452df10d9554c71`.

Continue the exact process, seed stream, optimizer, auxiliary coefficient, and linear learning-rate
schedule to four million decisions.  Decide discovery only from the frozen final functional gate
and then the separately executed exact recipe-by-role action audit.
