# D153a conditional-second value policy cross-fit — frozen protocol

Date: 2026-07-23  
Status: frozen after D152 passed and wrote exact values, before any D153 fit

## Hypothesis and model

D149's one-hot argmax failed because 70.19% of exact conditional states contain a nonselected
near-tie and the sampled selected action is exact-best only 48.62% of the time. Replace hard winner
classification with exact value learning on all 909 groups and 16,228 actions.

Use one slim state-conditioned scorer: concatenate 64 state and 379 action features, then
`443 -> 16 ReLU -> 1` (7,121 parameters). Subtract each group's raw slot-zero score from every raw
score, making control exactly zero by construction. Express predicted and target values in units of
50 margin points.

Train with equal-weight sum of:

- within-group soft cross entropy at temperature 10 margin points, retaining all near ties; and
- per-group mean Smooth-L1 between predicted and exact conditional values over every legal action.

No separate gate or activity calibration is allowed: slot zero competes directly with noncontrol
actions and inference chooses the stable maximum score.

## Frozen selection

Use seeds `15301--15304`, 80 epochs, batch size 64, Adam learning rate `1e-3`, and weight decay
`1e-4`. Perform eight leave-one-8-map-fold-out fits per seed, so each of the 909 states is selected
out of fit exactly once. Use ten forked workers with two PyTorch threads each. Run the full
selection twice and require byte identity.

Evaluate policy value from the exact held terminal of the selected slot, not label accuracy. A seed
is eligible only if pooled held behavior has:

- at least `+5.0` mean exact conditional value over slot zero;
- at least 30% strictly positive selections and at most 15% harmful negative selections;
- at least 15% aggregate oracle-value capture and mean oracle regret at most 26;
- at least 20% of selections within ten margin points of the exact oracle;
- nonnegative mean selected value in every held fold;
- at least six positive opponent families and a family floor at least `-2`;
- action-value sign balanced accuracy at least 60% at predicted score zero;
- zero new crop failures relative to slot zero; and
- worker-three reach within five percentage points of slot zero.

Select eligible seeds by worst-fold mean value, family floor, pooled mean value, oracle capture,
within-ten rate, lower harmful rate, then lower seed.

After an eligible byte-identical repeat, fit the selected seed twice on all folds and require equal
canonical hashes, 7,121 finite parameters, then save one checkpoint.

## Decision boundary

Passing opens D154 first-stage value construction using D150's rich population support and D152's
exact downstream second values. It does not yet open prospective validation: a conditional-second
policy alone cannot choose its first setup action. Failure closes this compact representation or
objective before any new maps.

D153 cannot read/generate reserved maps `9,844,200--9,844,215`, integrate Rust, qualify or submit a
candidate, change the resident, or interact with Arena.
