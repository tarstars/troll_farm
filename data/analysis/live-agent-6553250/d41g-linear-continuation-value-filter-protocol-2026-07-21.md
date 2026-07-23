# D41g compact linear continuation-value filter — frozen discovery protocol (2026-07-21)

## Question and scope

D41f shows that early/late rank-one rate proposals from residual gap 0.200 through 0.340 have strong
positive mean value but only 57% positive outcomes. D41g asks whether a compact outcome-blind linear
score over the existing state/candidate features can remove enough negative actions while retaining
more coverage than D41e's 0.280 cutoff.

This is consumed-label model discovery. It authorizes exact feature extraction, grouped
cross-validation, the frozen model/threshold matrix below, an external consumed-bank replication,
tests, artifacts, and written analysis. It authorizes no new simulator outcome, complete-policy
run, confirmation, deployment candidate, TestSession, submission, or Arena.

## Frozen data roles

- Training/model-selection labels: the 600 D41f rows on maps 9,772,000--9,772,031, continuation-row
  SHA-256 `3bbc1c62a5383c3d8667c40ba7173026ded60721ec41d0db72fb6d021fe09d26`.
- External replication only after model selection: D41d early/late `rate` rows with residual gap in
  [0.200,0.340], from row SHA-256
  `be1181bbcdb4e5188f19f80377e111803d4a261ad90a4c469928869516559f53`.
- Frozen checkpoint and environment remain
  `1de76fc...71671a` and `5839a7b...70173` respectively.

D41d labels have been summarized previously, so replication is diagnostic rather than a sealed
confirmation. D41e prospective rows may not train or select the model.

## Exact 100-feature representation

Replay each manifest state under exact D40 and validate task, decision ordinal, turn, branch,
candidate count, teacher action, rank-one action, and stored residual gap. Construct, in order:

1. rank-zero shared features 0--16: 17 values;
2. rank-zero candidate features 17--43: 27 values;
3. rank-one candidate features 17--43: 27 values;
4. rank-one minus rank-zero features 17--43: 27 values;
5. frozen residual gap: one value; and
6. candidate count divided by 768: one value.

Total: exactly 100 float features. Opponent name/index, map, seat, task ID, terminal score, outcome,
hash, and cohort/bin label are forbidden model inputs. They remain metadata for grouping/audit only.

## Grouped model matrix

Use eight folds defined by `(map_seed - 9,772,000) mod 8`; all seats, opponents, and states from a
map stay in one fold. Standardization is fit on each training fold only. Fit ridge linear models
with an unpenalized intercept for each target:

- raw margin clipped to [-100,+100];
- margin clipped to [-50,+50]; and
- positive indicator (`margin > 0`) as 1, otherwise 0.

For each target use ridge alpha `0.1, 1, 10, 100`, giving 12 models. Produce exactly one
out-of-fold score per D41f row. Eligibility is frozen to early/late rate and residual gap
[0.200,0.340]. For each model evaluate score thresholds at selected-share targets
`40%, 50%, 60%, 70%, 80%` of eligible out-of-fold rows.

A cross-validated candidate passes only if it has:

1. at least 240 selected rows and at least 64 with gap below 0.280;
2. mean paired margin at least +12 with lower descriptive 95% bound above +8;
3. positive rate at least 65% and negative rate at most 27%;
4. early mean at least +14 and late mean at least +5;
5. positive mean in all eight held-out map folds;
6. at least six positive opponent means and none below -10.

Select the passing combination with the highest lower bound, then higher sample count, then lower
alpha, target order above, and lower selected-share target. Fit that model to all D41f rows and
convert standardized coefficients into one raw-feature bias plus 100 weights. Set its production
threshold to the full-training score quantile that reproduces the selected out-of-fold share.

## External replication gate

Apply the frozen raw weights and numeric threshold to eligible D41d rows without refitting. Require:

1. at least 64 selected rows, including at least 24 below gap 0.280;
2. mean margin at least +8 with lower descriptive bound above zero;
3. positive rate at least 60%;
4. both early and late means positive; and
5. at least five positive opponent means with none below -15.

The model qualifies only if both grouped discovery and external replication pass, extraction is
exact, coefficients are finite, raw-versus-standardized predictions agree within `1e-5`, and the
kernel estimate is at most 101 scalar parameters.

A pass opens a separate prospective complete-policy protocol beginning at maps 9,773,000. A fail
closes this linear representation; do not tune hidden variants on either consumed bank.
