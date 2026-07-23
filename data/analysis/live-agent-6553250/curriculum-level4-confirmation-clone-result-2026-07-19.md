# Curriculum Level 4 independent confirmation clone — 2026-07-19

## Verdict

Pass. The independently seeded transfer clone clears every frozen clone gate on exact seeds
2,017,000--2,018,999. This authorizes the unchanged seed-89 confirmation PPO run; it does not
accept Level 4, alter the resident, establish opponent transfer, or authorize an Arena submission.

## Prospective functional result

The clone starts from the accepted Level-3 confirmation checkpoint, not the Level-4 discovery
checkpoint. It consumes exactly 800,000 online teacher decisions from stream 6,800,000.

| Metric | Confirmation clone | Frozen clone gate | Result |
|---|---:|---:|:---:|
| Overall success | 1,961/2,000 (98.05%) | >=70% | pass |
| Nontrivial success | 98.11% | >=65% | pass |
| Worst recipe success | 96.12% | >=55% | pass |
| Worst height success | 97.41% | >=60% | pass |
| Tracked crop created | 98.30% | >=75% | pass |
| Renewable harvest | 98.60% | >=65% | pass |
| Paired teacher median delay | 0 turns | <=45 turns | pass |

Median training/completion turns are 14/52 and median post-training score gain is 15. Teacher
generation completed 8,619/8,621 episodes. Every reported loss is finite.

The clone took 589.50 wall seconds and 7,685.77 process CPU-seconds, equivalent to 65.19% of the
20-logical-CPU host.

## Reproducibility anchors

- frozen protocol:
  `ea4c66a270effb9040db17b2476e61bcf88f1edf2719051f6ffea42571022596`;
- accepted Level-3 initial checkpoint:
  `a0a0f4bd590175d45be4ec63a8394a47cbe475187d942906d4e01038a167b0df`;
- confirmation clone checkpoint:
  `a5aab5d22a667268316ab620767964f2f9a088af9e545a14f7993511a4780ead`;
- exact evaluation:
  `6ffea3913fcb146f40c202ca3a48b4af8877f94ce1a3d9760f8a11f121aab903`;
- training summary:
  `516d54c1d0db6a66edf5214867bbf760d8a8cb389a17958b1e2444259865cb90`.

## Authorized next execution

Run the frozen seed-89 confirmation PPO from stream 6,900,000 with the legal-only 0.10 teacher
auxiliary. Read Stage A at one million decisions and, if its stop gate passes, continue the same
process unchanged to four million. Level 4 is accepted only if the final exact functional and
recipe-by-role action audits both pass.
