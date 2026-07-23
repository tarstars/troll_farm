# D82a threatened-own-crop semantic response rollout — frozen protocol (2026-07-21)

## Question

D78's transferable behavior signal concerns imminent attacks on resident-owned crops. D80/D81
broadened that signal to any nearby crop and organized responses by generic prior rank; both closed
before value. Does a provenance-faithful semantic response set contain safe one-decision terminal
headroom over D40?

D82a is an exploratory exact-rollout upper bound. Realized support and value are both reported after
integrity; support controls advancement confidence but does not seal all outcome description. No
rollout arm is deployable or selectable.

## Frozen root and semantic arms

Follow exact D40 until the first `Rate` boundary containing at least one legal candidate that:

1. targets an `Own`-provenance crop (`candidate_feature[31] == 1`);
2. has current opponent distance to that target at most two (`D42 job_context[13] == 1`);
3. uses `FELL_BANK`, `HARVEST_BANK`, or `RENEW`; and
4. differs from D40's exact rank-zero action.

Independently replay four arms from the initial state:

- `control`: exact D40 at the root;
- `fell`, `harvest`, `renew`: the lowest exact-prior candidate satisfying the root predicate on that
  action plane, iff it differs from control; otherwise exact control.

Each available semantic arm changes exactly one decision and then returns to exact D40 through
terminal. All arms must reconstruct the same root. There is no rank cap, fitted coefficient,
target-health threshold, repeated intervention, or post-root policy change.

## Frozen execution

Use previously unopened official maps 9,914,000--9,914,031, both seats, and the unchanged eight D40
opponents: 512 tasks, four arms, and 2,048 rows per repeat. Run twice with 20 threads and require
byte identity. Maps 9,915,000--9,915,031 remain sealed.

Record exact terminal/mechanics/action fields, root identity, semantic arm availability, selected
exact-prior rank and action plane, one-decision budget, reward identity, maximum workers,
finite/legal/fallback failures, and action planes.

## Integrity gates

All are mandatory:

1. complete byte-identical 4 x 512 repeats;
2. zero invalid command, provenance, deposit-prediction, worker-cap, reward, finite-feature, legal,
   fallback, action-count, root-identity, or arm-accounting failure;
3. every unavailable semantic arm reproduces control exactly; and
4. every available semantic arm makes exactly one intervention and changes action hash.

Integrity failure quarantines value and permits only a defect repair.

## Support and safe-oracle gates

Report roots, available arms by semantic type/rank/plane, seats, maps, and opponent families. For
advancement require at least 128 rooted tasks, at least 32 available arms of each semantic type,
both seats, and all eight opponents. A support miss still permits descriptive value but fails the
overall conjunction.

For each task admit control and available semantic arms that create a crop and finish with at least
`max(2, control_workers - 1)` workers. Select maximum terminal margin, ties to control then
`harvest`, `renew`, `fell`. Require:

1. mean oracle margin gain at least +8;
2. strict improvement in at least 40% of rooted tasks;
3. mean own-score delta nonnegative or opponent-score delta nonpositive;
4. at least six opponent-family mean gains positive and the worst nonnegative;
5. at least two semantic arms are selected strictly in at least eight tasks each;
6. oracle crop creation is 100% and worker-three reach falls by at most five percentage points; and
7. every task retains the safe control arm.

## Decision rule

- **Support and oracle pass:** retain the provenance-specific semantic vocabulary and open D83, a
  bounded Monte-Carlo/value approximation on fresh maps.
- **Oracle failure:** close threatened-own-crop one-decision response search; commitment prediction
  does not translate into sufficient terminal response value.
- **Support failure:** preserve descriptive value but do not advance; change representation rather
  than expand maps or lower floors post-result.
- **Integrity failure:** quarantine value and repair only the defect before unchanged repeats.

No D82 branch authorizes candidate construction, TestSession, submission, or Arena activity.
