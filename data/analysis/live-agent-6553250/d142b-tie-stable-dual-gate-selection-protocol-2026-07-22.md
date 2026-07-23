# D142b tie-stable dual-gate selection — mechanics-repair protocol

Date: 2026-07-22  
Status: frozen after D142a's tied-boundary abort and before any D142b fit

## Isolated repair

Retain D142a's exact shared ranker, two source-reproducing gates, arithmetic float32 mean, losses,
seeds, eight blocks, +3pp target count, policy gates, selector, and execution. Replace only the
scalar representation of an activity boundary when equal logits straddle its quantile.

For every task, take the maximum exact mean gate logit and pair it with a stable priority: the
SHA-256 hex digest of the compact JSON task key. Sort pairs `(logit, priority)` descending and use
the Nth pair as an inclusive cutoff for N requested active tasks. A root is open exactly when its
pair is at least that cutoff. Convert this boolean to gate value 1 or 0 and use offset 0.5 in the
unchanged policy evaluator. Require unique priorities and an exact achieved training count.

For unequal logits this is equivalent to the inherited threshold. Priority affects only exact
ties, is derived without labels or held outcomes, and transfers unchanged to held panels. Record
the active-floor and inactive-ceiling pairs and whether the numeric boundary was tied.

## Decision

Run the same eight-fold selection twice and require byte identity. An eligible repeat permits one
all-eight-block fit and unchanged consumed-D126 veto. D126 cannot tune or rescue. Only a veto pass
opens separately frozen untouched validation. D142b cannot collect maps, integrate Rust, submit,
mutate the resident, or interact with TestSession/Arena.
