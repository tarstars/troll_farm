# D130a cross-sign pairwise soft ranker — frozen protocol

Date: 2026-07-22  
Status: frozen before D130 training or consumed-panel scoring

## Isolated hypothesis

D127 attributes 82/98 D126 losses to ranking a nonpositive proposal above an available positive
proposal. D128 shows that absolute value anchoring conflicts with relative ranking, and D129 shows
that an independent absolute-sign classifier does not transfer. Relative cross-sign order within
one root is translation-invariant and directly represents the failed decision.

Retain D119's exact 6,626-parameter factorized architecture, 379 action features, 64 state
features, temperature-10 soft listwise cross-entropy, state-gate BCE, equal-root batches, 80
epochs, Adam `1e-3`, weight decay `1e-4`, and one deterministic thread. Add one coefficient-1,
equal-root logistic pairwise term. Within every root containing both classes, average
`softplus(-(positive_logit - nonpositive_logit))` over every positive/nonpositive proposal pair;
then average equally over eligible roots. Do not change runtime inference.

Use fresh initialization seeds `13001--13004`. Require all unchanged D119 structural gates plus
at least 70% root-mean cross-sign pair accuracy and at least 50% positive-winner rate on mixed-sign
fit roots. Calibrate each state gate by the unchanged D125 84% fit-task quantile and require all
unchanged D118 fit-policy gates. Select eligible seeds only by minimum fit proposal regret, then
higher within-ten coverage and fixed seed order.

## Development and authority

Score exactly the one training-selected model on the consumed D126 panel with unchanged D126
relative gates. Do not scan coefficients, margins, thresholds, seeds, widths, or architectures.
Require two complete result artifacts to be byte-identical.

A full consumed-development pass may justify freezing untouched seeds `9,843,800--9,843,815` for
one fresh validation. Consumed data cannot qualify the model, emit a checkpoint, authorize Rust
integration, or trigger platform interaction. Any structural, fit-policy, or development failure
closes this exact pairwise formulation without tuning.
