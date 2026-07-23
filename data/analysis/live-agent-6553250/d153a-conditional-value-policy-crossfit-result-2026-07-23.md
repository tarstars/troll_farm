# D153a compact conditional value policy — result

Date: 2026-07-23  
Decision: **close this compact representation/objective**

The exact join is clean: 909 conditional-second groups, 16,228 legal actions, 15,319 noncontrol
actions, eight map folds, eight opponent families, and exact slot-zero controls. The frozen
`state64 + action379 -> 16 ReLU -> 1` model has 7,121 parameters and trains on equal-weight grouped
soft ranking plus Smooth-L1 relative value.

No seed passes held value. The best pooled mean is seed 15303 at **+1.820 margin**, versus the
frozen +5 threshold. It selects a harmful negative action in **44.44%** of states, captures only
**5.99%** of oracle value, has **28.56** mean oracle regret, and reaches only **50.995%** action-value
sign balanced accuracy. Its worst fold is -0.992. All four seeds lie in a narrow weak range:

| Seed | Mean value | Harmful | Oracle capture | Regret | Within 10 | Sign BA | Worst fold |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 15301 | +1.354 | 44.77% | 4.46% | 29.03 | 22.99% | 51.65% | -2.528 |
| 15302 | +0.858 | 45.43% | 2.82% | 29.52 | 23.87% | 51.47% | -1.650 |
| 15303 | +1.820 | 44.44% | 5.99% | 28.56 | 24.75% | 51.00% | -0.992 |
| 15304 | +1.119 | 45.87% | 3.68% | 29.26 | 23.10% | 50.79% | -2.890 |

Crop and workforce checks remain exact: zero new crop failures and 91.64% worker-three reach for
both control and selected terminals. Those safety passes do not rescue the value failure.

The repeated selections reproduce every held discrete decision and metric. One of 32 seed/fold
fits differs at tiny threaded floating-point scale on repeat (seed 15304/fold 1), so the raw JSON
and canonical model hash are not byte-identical. This independently fails the frozen repeat gate;
it does not change the negative behavioral verdict.

The key diagnosis is strong fit/weak transfer: training-fold policies select roughly +14--17 mean
exact value, while leave-one-map-fold-out behavior falls to +0.86--+1.82 and sign accuracy is
essentially chance. The compact snapshot scorer is learning fold-specific action/value structure
and almost never abstains (only 2.2%--2.9% control selections). Before increasing capacity or
building first-stage values, test whether out-of-fold score confidence contains a stable
high-precision region that can justify abstention. This is diagnostic only; it cannot create a
submission candidate or open the reserved panel.

No checkpoint is written. Reserved maps `9,844,200--9,844,215` remain sealed; no Rust integration,
Arena interaction, submission, or resident mutation occurred. Result JSON SHA: `0db54ee0...`.
