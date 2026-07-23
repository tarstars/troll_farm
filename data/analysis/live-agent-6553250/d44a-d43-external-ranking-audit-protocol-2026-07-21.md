# D44a D43 external action-value ranking audit — frozen protocol (2026-07-21)

## Question and scope

D43 moved the mean rank-one probability but failed its state-dependent movement gate. Its fixed
probe standard deviation was small rather than zero, so one consumed-data question remains before
closing the residual family: do those small score differences rank exact out-of-training
continuation value, or are they noise/a restatement of the frozen residual gap?

D44a is a read-only architecture diagnostic. It uses every already-consumed D42 continuation row
and the frozen D43 checkpoint. It opens no map, replay, model fit, optimizer step, policy rollout,
candidate, TestSession, submission, or Arena action. D42 remains rejected and cannot become
qualification evidence; its outcomes are used only to select the next learning abstraction.

## Frozen inputs

- D42 manifest, 1,087 rows:
  `d42-context-manifest-9773000-9773063.tsv`, SHA-256
  `6d7a09bcba26b3cc9a65e583d3b48699704a0dcab545a1d631404b0a13ffba3f`;
- D42 exact paired outcomes, SHA-256
  `fd7525314a272b6ce3b9b22788f46af08e7841ff8452b6eea4b17352f951a7a4`;
- D43 final checkpoint, SHA-256
  `ae25f7a889ffe74a203bccefdc1140bd5d436091d63f0342612a5ec02550b469`;
- D43 result JSON, SHA-256
  `12bac7491b67e118d9d90baf3895b8a1165b1f7b8335572956039608e352661e`.

No subset may be selected using outcomes. Export all 1,087 manifest rows in sample-ID order.

## Frozen 154-feature replay export

Replay D40 once per distinct `(map_seed, seat, opponent)` task and capture each manifest decision
before applying its D40 action. Verify decision ordinal, turn, branch, candidate count, rank-zero
action, and rank-one action exactly. Construct the unchanged D43 actor vector:

1. rank-zero shared features 0--16 (17);
2. rank-zero candidate features 17--43 (27);
3. rank-one candidate features 17--43 (27);
4. rank-one minus rank-zero candidate features (27);
5. mean legal-candidate features 17--43 (27);
6. maximum legal-candidate features 17--43 (27);
7. manifest-frozen residual gap and candidate count / 768 (2).

Require 154 finite `f32` values per row, all sample IDs exactly once, and complete replay of all
590 distinct tasks. Score the vectors with the frozen D43 actor; no calibration, sign reversal,
standardization, or threshold fitting is permitted.

## Frozen analysis

Use exact D42 `margin_delta` as the value target and D43 probability as the ranking score. Report:

- probability mean, standard deviation, range, and deterministic rank-one count;
- global Pearson and average-tie Spearman correlations;
- a 4,096-replicate map-cluster bootstrap 95% interval for Spearman, RNG seed 4,401;
- top/bottom half and quartile outcome summaries;
- top-half-minus-bottom-half margin contrast with a map-clustered normal interval;
- top-quartile map-fold, opponent, phase, and gap-cohort means;
- within-cohort ranking after subtracting each of the 12 phase × gap-bin means from both score and
  margin, plus the sign of the top-half contrast inside each cohort.

Top/bottom sets use stable `(score, sample_id)` ordering. With 1,087 rows, top half is the highest
544 and top quartile is the highest 272. No alternative cutoff is inspected.

## Frozen gates

D43 contains useful external state ranking only if every gate passes:

1. replay/identity/schema/integrity checks are exact and all 1,087 rows are finite;
2. external probability standard deviation is at least `0.0005`;
3. global Spearman is at least `0.08` and its map-cluster bootstrap lower bound is above zero;
4. top-half minus bottom-half mean margin is at least `+4.0`, its map-clustered normal lower bound
   is above zero, and at least six of eight map-fold contrasts are positive;
5. phase × gap residualized Spearman is at least `0.05`, and at least seven of twelve within-cohort
   top-half contrasts are positive;
6. the top quartile has at least 250 rows, mean margin at least `+10`, map-clustered normal lower
   bound above `+5`, positive rate at least 60%, and negative rate at most 30%; and
7. all eight top-quartile map-fold means are positive; at least six of eight opponent means are
   positive and the worst is at least `-10`; both phase means are positive.

## Decision rule

A conjunction pass authorizes only a separately frozen D44b iterative, on-policy counterfactual
policy-improvement preflight. That design must refresh paired action values under its current
policy and validate the complete policy prospectively; it may not fit or qualify on D42.

A failure closes D43 score reuse and this sparse binary residual family. Do not change the score
scale, reverse it, choose another quantile, weaken a gate, retrain D43, or fit D42 again. The next
cycle must move to a different action/horizon representation rather than another snapshot
rank-zero/rank-one selector.
