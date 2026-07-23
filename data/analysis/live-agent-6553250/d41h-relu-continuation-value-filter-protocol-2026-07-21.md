# D41h tiny-ReLU continuation-value filter — frozen discovery protocol (2026-07-21)

## Question and authorization

D41g's affine models rank expected magnitude strongly and generalize across maps, phases, and
opponents, but every model fails sign precision. D41h asks whether one bounded ReLU interaction
layer can separate negative continuations using the identical exact 100 features.

This protocol authorizes consumed D41g feature archives, the fixed model matrix below, grouped
cross-validation, deterministic full-model replay, external D41d replication, tests, weights, and
written analysis. It authorizes no new simulator outcome, complete-policy run, confirmation,
candidate construction, TestSession, submission, or Arena.

## Frozen data and representation

- D41f feature archive SHA-256:
  `881cbbe5c4a1c86eeb3954604d30889380671ffa4da4c7ec62e62659605d5f1b`;
- D41d external archive SHA-256:
  `c8c0aa33fc2c22406edff837c878fb95863ecee001fc5cb2f28c54e9e9128d69`;
- exact feature order is the D41g 100-vector; opponent identity remains absent;
- eight whole-map folds are unchanged.

No feature selection, cross term, opponent encoding, relabeling, resampling, or D41e outcome is
allowed.

## Frozen model matrix

Use `100 -> hidden ReLU -> 1` with hidden width 8 or 16. Train each of three targets:

1. margin clipped to [-50,+50] and divided by 50, mean-squared error;
2. positive indicator (`margin > 0`), binary cross-entropy with logits; and
3. nonnegative indicator (`margin >= 0`), binary cross-entropy with logits.

For each width/target use Adam, full batches, learning rate 0.01, exactly 600 epochs, and weight
decay `0.0001` or `0.01`: 12 configurations. Standardization is fit within each training fold.
Initialization seed is `431 + 100*target_index + 10*width_index + 1000*decay_index + fold`, where
fold is 0--7 and 8 denotes the final full-data fit. No early stopping or checkpoint selection.

For each configuration generate one out-of-fold score per D41f row. Within eligibility gap
[0.200,0.340], evaluate top score shares 50%, 60%, and 70% using deterministic threshold ties.

## Unchanged grouped gates and selection

A candidate must retain the D41g gates:

- n >=240 and at least 64 selected rows below gap 0.280;
- mean margin >=+12, lower descriptive bound >+8;
- positive rate >=65%, negative rate <=27%;
- early mean >=+14, late mean >=+5;
- all eight held-out map-fold means positive; and
- at least six opponent means positive with none below -10.

Select by highest lower bound, then higher n, smaller hidden width, stronger weight decay, target
order above, and lower share. Fit the selected configuration twice on all D41f rows using the fixed
full-data seed and require weights and predictions to be bit-identical. Convert the standardized
first layer to raw-feature weights and require prediction parity <=`1e-5`.

## External replication and size

Freeze the numeric threshold at the full-training score quantile reproducing the selected OOF share,
then apply once to D41d external features. Require the unchanged D41g external gates: n>=64,
at least24 below 0.280, mean>=+8 with lower bound>0, positive>=60%, both phase means positive,
and at least five positive opponent means with none below -15.

Maximum deployable scalar count, including threshold, is 1,634. A configuration qualifies only if
grouped discovery, deterministic repeat, raw parity, size, and external replication all pass.

A pass opens a separate fresh complete-policy protocol on maps beginning 9,773,000. A fail closes
this feature representation for consumed-label classification; do not add widths, epochs, losses,
seeds, or thresholds on these banks.
