# E7a half-size structural specialization fresh rejection — 2026-08-03

Status: **TERMINALLY REJECTED ON RESERVED FRESH TRANSFER GATE**

The immutable 31,337-byte source, SHA-256 `7fd755c2...`, was evaluated once on the
preregistered untouched block 9,854,043--9,854,085: 43 maps, both seats, six opponent
families, 516/516 unique continued-referee tasks. No source, threshold, evaluator, opponent,
or gate changed after lock `857f4cb`.

## Result

- mean paired margin: +3.3043 (passes);
- bootstrap 95% lower: **-6.3450** (fails > -2.0);
- catastrophes: 19 -> 14 (passes);
- negative-margin mass: **4,385 -> 4,891** (fails);
- family means: compact -4.698, gold +5.395, legend +7.477, mybot +6.116,
  norx +2.465, resident +3.070 (five of six pass);
- seats: +3.070 / +3.539 (both pass);
- worker-two coverage 100%, median delay 0;
- period-2 episodes >=6: 84 -> 0, candidate maximum 4;
- latency p95 ratio 0.843, maximum 1.829 ms;
- zero critical and zero unclassified outcomes.

Evaluator verdict: `REJECTED_OPEN_PANEL`. Exact evidence hashes:

- panel TSV: `7c84fcd57174fce084e87e025440fb79c6a87153e9b1ed60b07722f278adb1b0`;
- result JSON: `4a5b511698e9f4565d05d4614113b004b6d480c83f6918d99c0efa887ecb0101`.

## Descriptive concentration

Two roots dominate the transfer failure without changing its terminal status:

- 9,854,062: mean -82.667, negative-mass increase +326, one extra catastrophe;
- 9,854,065: mean -86.500, negative-mass increase +317, one extra catastrophe.

Together they contribute +643 negative mass, larger than the panel's net +506 increase.
Compact-gold is the only negative family overall, but the worst individual regressions span
compact, norx, gold, legend and resident, so this is not yet a single-opponent diagnosis.

## Disposition

The exact locked source cannot proceed to Arena and will not be tuned on these fresh maps.
The positive mean and complete liveness repair remain useful architectural evidence, not a
qualification result. A successor must be a distinct logical policy, use consumed data only
for development, freeze before another untouched block, and reserve a new sufficiently large
fresh range under a new lock.
