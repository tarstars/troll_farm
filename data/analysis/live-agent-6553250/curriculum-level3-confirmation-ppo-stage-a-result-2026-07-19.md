# Curriculum Level 3 independent confirmation PPO Stage-A result — 2026-07-19

## Verdict

Pass.  The unchanged seed-79 PPO clears every frozen one-million-decision safety gate on the new
exact confirmation bank.  Continuing the same process to four million decisions is authorized;
Level 3 and all live changes remain unauthorized until the final functional and action gates pass.

## Exact prospective metrics

Evaluation covers seeds 2,013,000--2,014,999 (2,000 episodes).

| Metric | Stage A | Frozen threshold | Margin |
|---|---:|---:|---:|
| Overall success | 1,963/2,000 (98.15%) | 65% | +33.15 pp |
| Nontrivial success | 97.81% | 60% | +37.81 pp |
| Worst height success | 97.21% | 55% | +42.21 pp |
| Tracked crop created | 98.40% | 70% | +28.40 pp |
| Renewable harvest | 98.35% | 60% | +38.35 pp |
| Paired teacher median delay | 0 turns | <=45 | 45 turns |

Height rates are 97.21% (8), 97.80% (9), 99.60% (10), and 98.00% (11).  Median
training/completion turns are 18/47 and median score gain is 16.

## Reproducibility anchors

- Stage-A checkpoint:
  `fce57139a04f9e1fae4988a133b62923a3dae03f3eabed8377ca7164fac99aa0`;
- exact Stage-A evaluation:
  `f30446068ca2e8e4a093d64fc480f68ef9440b834694882349ed70178b91a361`;
- independent clone checkpoint:
  `cbf7626290e1e64b583703da5397efb7db5b1bf76f86788a42716c37a6a61fbb`;
- corrected trainer:
  `e55a8cf1f1ff3b9bc77b8f24769d35cb89b3098e630574cbb4ab47abb83b4351`;
- frozen confirmation protocol:
  `d0e0c35cd2b86b3f14d5ba3675541578dcb21aba77e5c44334be341dc753f74d`.

The process, optimizer, stream, controls, and gates continue without intervention.
