# D122a D119 crop-failure trace — frozen protocol

Date: 2026-07-22  
Status: frozen after D121 retrospective metrics and before tracing selected actions

## Question

D121 finds exactly two crop failures in the useful D119 policies. Determine whether they are the
same tasks/actions, which runtime-observable state and proposal fields characterize them, and
whether the selected roots contained crop-safe alternatives. This is attribution, not policy
repair or candidate selection.

## Fixed trace

Reproduce all four D119 models and trace exact first-positive semantics for the complete frozen
24-policy grid on the consumed 80-map panel. Record each policy's crop-failure task set and the
frequency/overlap of unique failures. For every failure, record the selected boundary, proposal
kind/jobs/owners/actions/prior ranks, gate/rank scores, exact score deltas, control/outcome crop and
workforce fields, and a documented subset of the 64 runtime-observable state features.

At each failing root, list crop-safe proposals ranked by the same model and the exact best safe
alternative. These alternatives use terminal labels and are oracle diagnostics; they are not a
deployable shield and must not be reported as a policy result. Focus summaries are frozen for the
locked policy, seed11903 offsets -1/-0.5/0, and seed11904 offset 0, but all 24 are traced.

## Decision boundary

D122 may generate a prospective safety-head or observable-rule hypothesis to fit on training data.
It cannot choose an offset, edit D119, qualify a candidate, integrate Rust, use Arena, submit, or
mutate the resident.
