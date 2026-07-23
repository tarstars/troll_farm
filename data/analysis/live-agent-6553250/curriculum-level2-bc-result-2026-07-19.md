# Curriculum Level 2 behavior-clone result — 2026-07-19

## Verdict

**Pass.**  The frozen seed-61 clone learns all eight requested worker families strongly enough to
open teacher-anchored PPO on the new exact bank.  No family is hidden by reset-affordable episodes.

This is a curriculum result only; it does not change the resident or authorize Arena submission.

## Exact consumed-bank result

After 400,000 online teacher labels, the deterministic clone scores on exactly seeds
2,003,000--2,004,999:

| Metric | Required | Observed | Result |
|---|---:|---:|---|
| Overall success | >=80% | 89.90% | pass |
| Nonzero-total-deficit success | >=75% | 83.17% | pass |
| Recipe-family floor | >=70% | 79.17% | pass |
| Height floor | >=65% | 87.82% | pass |
| Paired teacher median delay | <=20 turns | 0 turns | pass |

Family success is 99.23% cheap-planter, 97.67% compact-farmer, 95.79% balanced-producer, 81.95%
harvest-producer, 98.28% Level-1 anchor, 83.74% lean-chopper, 82.77% standard-chopper, and 79.17%
hybrid-chopper.  Errors therefore concentrate in recipes needing APPLE and/or IRON in addition to
movement/carry funding, as expected from the abstraction increase.

The final online chunks reach roughly 92--95% teacher-action accuracy.  Labels contain 328,441
MOVE, 31,544 HARVEST, 35,756 DROP, and 4,259 MINE actions.  Training takes 700.47 seconds wall,
8,407.99 CPU-seconds, and about 60.0% aggregate 20-core host capacity.

## Frozen artifacts

- checkpoint: `3fe89cca6453a733a5a41703498de098280ba6bf084c407ddbfd00a6f44c95dd`;
- exact evaluation: `72fc979676671b48c5d6764fc7c621aee1291e356f00bf31b1b1c11313c93b76`;
- training summary: `7b62a1dd36cd0ae0e5ce313dfe6ad390d167bdb6a380f3212786550cc2f5b374`;
- fresh teacher control, seeds 2,005,000--2,006,999:
  `a442a23b5e6603d89097923980aa800cb4af85582d2278fa846ceac0b604d605`;
- fresh random control, same interval:
  `b5e18106f5fed9fd807d1eb66b0269fd9e6705beff14f3737735fff2759e36a8`;
- PPO trainer at launch: `4caae4070906f74883521212fbe35a924ca9ee3ae057665b4f1ff99d060e3546`.

## Next move

Start the frozen two-million-transition PPO discovery from this exact clone, with stream 5,100,000
and teacher auxiliary coefficient 0.10.  Evaluate Stage A at 500,000 transitions on the untouched
2,000-seed bank; stop automatically if overall, nontrivial, recipe-floor, height, or teacher-delay
gates fail.
