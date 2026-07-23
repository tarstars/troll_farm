# D41d residual-ranked one-deviation continuation — result (2026-07-21)

## Verdict

**Reject a global residual override, but open a branch-gated follow-up for `evacuation` and
`rate`.** The residual-top cohort improves mean paired terminal margin by **+4.555** across 578
fresh interventions, versus **+1.051** for 273 outcome-blind hash controls. Its descriptive normal
95% lower bound is +2.246 and its advantage over control is +3.504. The global gate nevertheless
fails because only 46.37% of interventions are positive, below the frozen 55% floor.

Two independently preregistered branch gates pass:

| D40 branch | n | mean margin delta | median | positive | normal 95% low | verdict |
|---|---:|---:|---:|---:|---:|---|
| evacuation | 64 | **+12.156** | +5 | **59.38%** | **+4.199** | pass |
| rate | 192 | **+6.760** | +4 | **57.81%** | **+2.681** | pass |
| deficit | 132 | +5.167 | 0 | 43.18% | +0.419 | fail positive rate |
| train | 190 | -0.658 | 0 | 32.63% | -4.334 | fail |

This is causal simulator evidence for isolated rank-one actions followed by exact D40, not a
qualified policy or Arena predictor. No temperature change, learned selector, candidate,
TestSession, submission, or Arena action is authorized by D41d.

## Frozen execution and integrity

The outcome-blind manifest was built from uninterrupted D40 trajectories on official maps
9,760,000--9,760,031, both seats, and eight opponents. It censused 80,364 decisions, of which
51,480 had a rank-one alternative, then selected 851 unique states by branch, phase, and opponent:
up to eight highest D41c residual gaps plus four deterministic hash controls per stratum.

The Rust runner reconstructed all selected states, validated turn, branch, candidate count,
teacher action, and rank-one action, took exactly one alternative, and returned to D40 through
terminal. All 851 rows are valid:

- zero invalid direct commands, provenance failures, relevant deposit-prediction failures, or
  worker-cap failures;
- two independent 64-row A/A executions are behaviorally identical; and
- the A/A rows exactly match the corresponding full-run subset after excluding elapsed time.

The complete continuation run covered 360 unique baseline tasks and completed in 74.269 seconds
with parallel treatment execution.

## Multilevel analysis

### Proposal ranking

The strongest learned residual preferences contain real action-value information: the top cohort's
mean is +3.504 above its hash control and all eight opponent-family means are positive, ranging
from +1.732 against `legend_balanced` to +10.528 against `compact_gold`. The D41c residual therefore
did not learn pure logit noise even though the fixed rank gap prevented any deterministic action.

The signal is not globally reliable. Residual-top outcomes range from -94 to +148 and 33.56% are
negative. A blanket temperature reduction would activate train and deficit decisions that fail
their frozen reliability gates alongside the two useful branches.

### Mechanism

The strongest signal lies where D40 already delegates to productive scheduling:

- `evacuation`: rank one usually replaces the shortest non-idle shack-clearing job with the next
  exact-prior alternative; it improves both median and mean continuation value;
- `rate`: rank one relaxes one lexicographic choice in the work-conserving job order and produces a
  broad positive distribution; and
- `train`: changing the exact worker-count/turn goal is not supported and must remain frozen.

Phase alone is insufficient. Early interventions average +8.641 and late +4.315, but middle
interventions average -0.729. Because the manifest is stratified and top-selected, these descriptive
phase effects cannot be deployed directly without a fresh prospective policy test.

### Representation and optimization

D41b's exact prior remains the correct safety anchor. D41c's residual is useful as a proposal ranker
but not as a calibrated policy logit: its scale was too small to act, while unconditionally
amplifying it would violate D41d's global gate. The next learning problem is therefore selective
continuation-value prediction, not another global PPO temperature sweep.

## Decision and next experiment

Open D41e under a new frozen protocol with these constraints:

1. preserve exact D40 behavior for `train` and `deficit`;
2. consider only D41c's exact-prior rank-one proposal in `evacuation` and `rate`;
3. derive an outcome-blind confidence rule from state and candidate features using only consumed
   D41d labels, with grouped validation that prevents map/task leakage;
4. freeze the selector and all thresholds before any fresh outcome is observed; and
5. evaluate the resulting complete closed-loop policy on a disjoint development bank against exact
   D40, with breadth, tail, workforce, crop, determinism, and disagreement gates.

If no discovery rule has stable held-out advantage, close this residual checkpoint as a deployable
selector and expand the proposal/action-value dataset instead. Confirmation maps 9,720,000--
9,720,031, candidate construction, and platform activity remain sealed.

## Evidence

- protocol SHA-256: `87bf7be940f61603e1f8042aa808f85fc9310fa4a221e26c8527859ec8806b62`;
- manifest summary SHA-256: `0fae399f19dc3a3b6c4c479c672aa6c01883b30d3b9d4246a9c61b897545c2ce`;
- continuation rows SHA-256: `be1181bbcdb4e5188f19f80377e111803d4a261ad90a4c469928869516559f53`;
- analysis JSON SHA-256: `f4ccbc56a4a013932e1cec1657131a8c4a451a4d55656c5be29a2564e688a24c`;
- A/A SHA-256: `63a08351feb5b4fafc4df7a6f2f5ec0d13ea85ae82b6219cc15477f36148d813`
  and `40cb28ffbae357fe8374b094ea45aba7ce7662bdb112dfa11ec72d25dfc01520`;
- focused Python verification: four tests pass.
