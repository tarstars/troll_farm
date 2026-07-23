# D79a spatial target/job scorer population result (2026-07-21)

## Verdict

**Reject and close the unconstrained all-Rate spatial scorer and its initialization.** The
implementation is exact, deterministic, mechanically clean, safe, and strongly outcome-sensitive,
but every one of the 32 random policies changes the action hash in **64/64 tasks**. Thus zero
policies enter the frozen 10%--90% task-activity corridor versus 24 required.

Do not shrink the weights, change the prior coefficient, narrow the population after seeing the
result, select a descriptively favorable random policy, or open D80 whole-policy optimization.
D79 is a consumed-map representation preflight; none of its random policies is a candidate and no
platform action is authorized.

## Integrity and exact anchor

- Both complete 33 x 64 matrices are byte-identical at SHA-256
  `ea9171638360ef4cbe635592b4af732026ceaf70ba4124b4edd3f560c7eae6b3`.
- The 889-parameter population reconstructs exactly from NumPy PCG64 seed 7901; the serialized
  catalog SHA-256 is `19c09391398e1441dd89b2a3d94acc13ffbbff62b75e3385c0afd7389f382895`.
- The zero policy matches the exact 64-task D40 prefix in every terminal, mechanics, action-plane,
  action-hash, and state-hash field: zero parity failures.
- Across 2,112 games there are zero illegal commands, provenance failures, deposit-prediction
  failures, worker-cap violations, reward-identity errors, nonfinite features/scores, illegal
  selections, or telemetry inconsistencies.
- The two 20-thread executions finish in 124.184 and 127.120 seconds while using about 19.6 CPU
  cores. Three Rust and six focused Python generator/analyzer tests pass; the wider D61p/D78/D79
  focused suite passes 15 tests.

## Frozen gate result

The sole failed gate is activity locality:

| Gate group | Result | Requirement | Verdict |
|---|---:|---:|---|
| Action-hash activity | 0/32 in 10%--90%; all are 100% | >=24/32 | **fail** |
| Override + action-plane activity | 32/32 | >=24/32 | pass |
| Opponent-near target activity | 32/32 | >=24/32 | pass |
| Crop safety | 30/32 at >=95% | >=24/32 | pass |
| Worker-three safety | 32/32 | >=24/32 | pass |
| Random mean-margin span | 118.141 | >=30 | pass |
| Means around anchor | 5 above / 27 below | both sides | pass |
| Safe oracle mean gain | +92.000 | >=+20 | pass |
| Safe oracle strict improvement | 59/64 = 92.19% | >=50% | pass |
| Safe oracle score decomposition | own +47.656 / opponent -44.344 | either side favorable | pass |
| Opponent-family oracle breadth | 8/8 positive | 8/8 | pass |

Every random policy executes at least 2,090 Rate overrides over the 64-task panel, and some execute
more than 4,400. Selected prior ranks reach as high as 123. The residual therefore overwhelms the
normalized rank spacing often enough that even otherwise safe policies become globally different
controllers, not local D40 corrections.

## Outcome sensitivity and non-selection warning

The D40 anchor averages +23.188 margin. Random fixed-policy means span **-71.609 to +46.531**;
five are descriptively above the anchor. These are consumed population members and cannot be used
as initializers, finalists, candidates, or evidence that any particular weight vector transfers.

The crop- and workforce-safe per-task hindsight oracle gains +92.000 margin, improves 92.19% of
tasks, raises own score by 47.656, removes 44.344 opponent score, and gains from +35.250 to +157.625
across all eight opponent families. This is valid representation headroom, but the protocol makes
activity locality a prerequisite to optimization. The oracle cannot rescue the failed conjunction.

## Multilevel interpretation

1. **Observability:** D78's conclusion survives contact with whole games. Current target condition,
   geometry, and opponent proximity participate in policies with broad outcome variation.
2. **Representation:** scoring every legal concrete job is expressive, but the normalized
   all-candidate rank residual gives a random network too much authority at too many boundaries.
3. **Safety substrate:** fixed D40 TRAIN, deficit, evacuation, persistence, reservations, and
   transactions preserve crops and workforce even under thousands of Rate overrides. They remain
   the correct anchor.
4. **Optimizer readiness:** a search over this population would conflate thousands of interacting
   deviations and could converge through batch-specific trajectory replacement. The failed
   locality gate correctly prevents that expensive and weakly identifiable branch.
5. **Action abstraction:** the next controller must expose a small, explicit concrete-target
   decision rather than another global four-mode scheduler or an all-Rate score over every job.

## Next experiment

Freeze a qualitatively different sparse target-intervention preflight. Preserve exact D40 outside
an explicit, auditable contested-crop boundary; compare a small concrete challenger set against
the D40 choice and allow at most a preregistered number of interventions per episode. The first
stage must establish activation inside a task-level corridor, exact mechanics, and causal paired
value before any learned selector or Monte-Carlo controller is trained.

This is not a post-result D79 rescale: it changes the action interface and intervention budget.
Existing D41-D44 rank-one snapshot classifiers, D61-D77 four-mode controllers, and D79's broad
scorer remain closed.

## Evidence

- protocol SHA-256: `fbbc571ceaaa705ebb004c16af4f73907c16f644a235d82a744e73590a1509b4`;
- result JSON SHA-256: `fa9828934fa51f4e7f346a1e96c138bf71bdf611bcd76570b8393b88ebc77490`;
- repeated matrix SHA-256: `ea9171638360ef4cbe635592b4af732026ceaf70ba4124b4edd3f560c7eae6b3`;
- population SHA-256: `19c09391398e1441dd89b2a3d94acc13ffbbff62b75e3385c0afd7389f382895`;
- runner SHA-256: `1b4a54f07f314b71b9998c33c2e7fc4d086feb976074dafec4e641bda6fdaa8d`;
- generator SHA-256: `fb8b8be1a7f3932c78401d0e09612bbcdbd5c7e38a33dec39bdbad5ed63833ee`;
- analyzer SHA-256: `79dfda46495aa25b3c000abbde8858170e5c282619186f55f1cecb264223accb`.
