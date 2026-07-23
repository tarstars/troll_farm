# D113a control-aware dense q6 teacher — frozen protocol

Date: 2026-07-22  
Status: frozen before any D113 outcome exists

## Causal change

D112a validates 13,377 exact q6 continuations and its snapshot repair byte-for-byte, but stops
before value analysis because 6/128 tasks expose no eligible paired q6 boundary while the frozen
protocol required universal support. Four such games finish normally without a paired proposal;
two terminate early with one worker. At runtime these episodes cannot invoke a q6 scorer, so their
correct behavior is forced D40 control, not rejection as malformed data.

D113 changes only that task-level support definition. A zero-boundary task contributes zero oracle
gain, its exact D40 outcome to safety, and no arm-level training labels. Every supported root and
arm retains D112's exact semantics. The offline backward rule remains
`V[t] = max(V[t+1], max_a G[t,a], 0)` and each arm target remains `G[t,a] - V[t+1]`.

## Immutable execution

Use untouched seeds `9,843,200--9,843,207`, both seats and all eight opponents: 128 tasks. Searches
found no prior artifact using this range. Use the unchanged repaired D112 collector, q6 expert
bank, 64 representatives, 64 state features, 379 control-relative action features, exact D40
control, one paired intervention, 20 workers, and complete terminal continuations.

D112 already proves three-way byte equality over a full 13,377-arm panel, including equality to
the pre-repair prefix-replay implementation. D113 therefore runs its fresh panel once; another
identical execution would add no new causal evidence. Require at least 12 arms/s.

## Frozen gates

### Mechanics and support

- exactly 128 unique baselines on the prescribed task grid;
- every declared root contains exactly `proposal_count - 1` unique noncontrol slots, every task's
  root indices exactly cover `0..boundary_count`, and zero-boundary tasks have no arm rows;
- at least 90% of tasks expose a root, with at least 600 roots and 6,000 arms overall;
- finite 64-value states and nonzero finite 379-value action differences;
- paired-gain error at most `1e-6`, reward identity below `1e-4`, exact one-use/joint accounting,
  and zero direct-command, provenance, or deposit-prediction failures;
- exact frozen inputs and at least 12 arms/s end-to-end.

### Teacher signal

Evaluate all 128 tasks, assigning no-intervention gain zero to unsupported tasks. Keep every D112
threshold unchanged:

- mean one-use oracle margin gain at least `+20`, strict gain on at least 75% of tasks, at least
  seven positive family means, and worst family at least `+8`;
- oracle mean own-score gain nonnegative or mean opponent-score gain nonpositive;
- act-now roots between 5% and 90% of supported roots;
- positive arm advantages between 1% and 50%, at least 40% negative, and target standard deviation
  at least five score points.

### Oracle safety

Across all 128 oracle outcomes, including exact control for unsupported tasks, require 100% crop
creation and worker-three reach within five percentage points of D40.

## Decision

- **Mechanics/support failure:** close the current q6 support definition without value analysis.
- **Signal/safety failure:** close this exact one-use dense-teacher formulation without fitting.
- **Full pass:** open D113b on new train/validation maps; fit a small regularized deployable scorer
  to act-now-versus-wait targets, then qualify it closed-loop on a separate untouched panel.

D113a creates no agent candidate and authorizes no TestSession, Arena, submission, or resident
mutation.
