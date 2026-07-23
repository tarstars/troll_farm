# D128a absolute-value-anchored soft ranker — frozen retrospective protocol

Date: 2026-07-22  
Status: frozen before D128 training or consumed-panel scoring

## Isolated hypothesis

D127 attributes 82/98 D126 losses to choosing a negative proposal while a positive proposal exists
at the same root. D119's soft listwise cross-entropy learns relative order but is invariant to an
additive logit shift, so the selected logit's sign has no safety meaning.

D128 retains the exact 6,626-parameter factorized architecture, 379 action features, 64 state
features, temperature-10 soft rank targets, state-gate BCE, equal-root batches, 80 epochs, Adam
`1e-3`, weight decay `1e-4`, one deterministic thread, and the D125 84% state-gate quantile. Add
exactly one root-balanced smooth-L1 term of coefficient 1 from proposal logits to
`act_advantage / 10`. At runtime a root is eligible only when its state gate passes and the
ranker's winning logit is strictly positive.

Use fresh initialization seeds `12801--12804`. Require the unchanged D119 regret/within-ten and
state-gate structural gates, plus at least 60% balanced accuracy and both recalls at least 50% for
the proposal-value sign (`max predicted logit > 0` versus `best exact advantage > 0`). Require the
unchanged D118 fit-policy gates after the value shield. Select among eligible seeds only by minimum
proposal regret, then higher within-ten coverage and fixed seed order.

## Retrospective development audit

Score exactly the one training-selected model on the consumed D126 panel with the unchanged D126
relative gates. Do not scan value thresholds, gate targets, loss coefficients, seeds, widths, or
architectures. Require two complete artifacts to be byte-identical.

A full retrospective pass may justify freezing untouched seeds `9,843,800--9,843,815` for one
fresh validation. The consumed panel cannot qualify the model, create a checkpoint, authorize
integration, or trigger platform interaction. A structural, fit-policy, or retrospective failure
closes this exact value-anchor formulation without tuning.
