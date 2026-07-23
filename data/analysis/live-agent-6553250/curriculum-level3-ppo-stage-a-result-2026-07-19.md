# Curriculum Level 3 corrected PPO Stage-A result — 2026-07-19

## Verdict

Pass.  The amended finite teacher-auxiliary run clears every frozen one-million-decision gate on
the exact prospective bank.  Continuing unchanged to four million decisions is authorized; Level
3, confirmation, live transfer, and submission remain unauthorized.

## Prospective metrics

Evaluation covers exact seeds 2,011,000--2,012,999 (2,000 episodes).

| Metric | Stage A | Frozen threshold | Margin |
|---|---:|---:|---:|
| Overall success | 1,969/2,000 (98.45%) | 65% | +33.45 pp |
| Nontrivial success | 98.06% | 60% | +38.06 pp |
| Worst height success | 98.20% | 55% | +43.20 pp |
| Tracked crop created | 98.60% | 70% | +28.60 pp |
| Renewable harvest | 98.65% | 60% | +38.65 pp |
| Paired teacher median delay | 0 turns | <=45 | 45 turns |

The four height buckets score 98.40% (8), 98.40% (9), 98.20% (10), and 98.80% (11).  Median
training/completion turns are 18/47 and median post-training score gain is 16.

The corrected run passed through the original non-finite failure region with explicit undefined-
label counts and finite auxiliary losses.  The replacement therefore validates both the renewable
hypothesis and the narrow numerical amendment at Stage A.

## Reproducibility anchors

- Stage-A checkpoint:
  `dfdb11eac7d0d93ddf75dccae9bfce762c642b8d263188ff6df1bce69c549100`;
- exact Stage-A evaluation:
  `a7e5cc262262bd4c9ffab8787345cf1df635cdd93e2e18fb761fe50ef50f02d8`;
- corrected trainer:
  `e55a8cf1f1ff3b9bc77b8f24769d35cb89b3098e630574cbb4ab47abb83b4351`;
- frozen amendment:
  `01b8cc5f40ce2a123e0d9e998c8bf987db935f9e1c25dede7af39c8192a07ed2`.

The same process, optimizer, stream, controls, and gates continue without intervention to the
four-million-decision final evaluation.
