# D156a hierarchical semantic value policy — frozen protocol

Date: 2026-07-23  
Status: frozen after D155a closed static history MLPs, before decoding semantic classes or returns

## Hypothesis

Exact target-cell outcomes may be too noisy for 909-state per-action regression while coarse macro
jobs remain stable. Decode only deployable semantics from each noncontrol action delta: proposal
kind, each worker's deviating job and owner, and prior-rank quartiles. Never use opponent identity,
map seed, fold, terminal information, or exact target coordinates as inputs.

State strata use current phase (thirds from state 56), rounded own workers (state 2), own-crop bucket
`1 / 2--3 / 4+` (state 58), and previous proposal kind (state 60--63).

For every held fold, estimate exact conditional value on the other seven folds. All empirical means
use a zero prior with 16 pseudo-observations. Hierarchical estimates shrink fine classes with 16
pseudo-observations at each parent level. Compare:

1. `jobs`: proposal kind + two job classes;
2. `job_owner`: jobs + two owner classes;
3. `job_owner_phase`: phase -> job/owner;
4. `job_owner_phase_rank`: rank quartiles -> phase -> job/owner;
5. `job_owner_regime`: workers/crops/previous-kind -> phase -> job/owner;
6. `job_owner_phase_lcb`: phase hierarchy minus 0.5 posterior standard deviation;
7. `job_owner_regime_lcb`: regime hierarchy minus 0.5 posterior standard deviation.

Within a held group, choose the stable highest-scored noncontrol class only when its score is
strictly positive; otherwise choose slot zero. Run the complete eight-fold calculation twice in
memory and require exact counts and scores. Report class cardinality/support and selected-class
support.

## Frozen readout

Apply every original D153 held gate. This is a discovery abstraction audit, so a pass opens a
separately frozen fresh-nonreserved-map confirmation, not a checkpoint or submission. If all
variants fail, close static empirical class value and prioritize online rollout/search or genuinely
recurrent policy control.

## Boundary

D156a cannot read/generate reserved maps `9,844,200--9,844,215`, collect maps, use YT, integrate
Rust, save a checkpoint, qualify or submit a candidate, change the resident, or interact with Arena.
