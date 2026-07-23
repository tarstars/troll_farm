# D81a one-boundary contested action-set rollout — frozen protocol (2026-07-21)

## Question

D80 shows that a first top-four contested-crop boundary exists in nearly every task, but correctly
stops before value because blindly forcing one challenger is not selective. At that same bounded
one-decision horizon, does the concrete action set contain enough crop/workforce-safe terminal
headroom to justify a future Monte-Carlo or learned value selector?

D81a is an exact deterministic counterfactual rollout upper bound. It cannot select a deployable
arm, fit a model, construct a candidate, open confirmation, or touch the platform.

## Frozen root and arms

Follow exact D40 until the first `Rate` boundary where exact-prior rank zero is not a contested crop
job and at least one of ranks one through three is. A contested crop job is unchanged from D80:
action plane `FELL_BANK`, `HARVEST_BANK`, or `RENEW`, with current opponent distance to the target
at most two (`D42 job_context[13] == 1`).

Independently execute four complete arms from the initial state:

- `control`: choose D40 rank zero at the root;
- `rank_1`, `rank_2`, `rank_3`: choose that exact rank iff it is a contested crop job at the root;
  otherwise reproduce control.

Every arm follows exact D40 before the root and immediately after its one root decision through
terminal. Thus all available noncontrol arms make exactly one intervention; there is no repeated
override, scorer, parameter, fitted D78 coefficient, rollout truncation, or post-root policy
change. The four independently replayed root identities must agree exactly.

## Frozen execution

Use previously unopened official maps 9,912,000--9,912,015, both seats, and the unchanged eight
D40 opponents: 256 tasks, four arms, and 1,024 rows per repeat. Run twice with 20 threads, sort by
`(arm, map_seed, seat, opponent)`, and require byte identity. Maps 9,913,000--9,913,031 are sealed.

Record exact D40 terminal/mechanics/action fields, reward identity, maximum workers, root
turn/state/candidate count, arm availability/rank/action plane, intervention count, finite/legal /
fallback failures, and action planes.

## Frozen integrity and support gates

All must hold before oracle value is interpreted:

1. complete byte-identical 4 x 256 repeats;
2. zero invalid command, provenance, deposit-prediction, worker-cap, reward, finite-feature, legal,
   fallback, action-count, root-identity, or arm-accounting failure;
3. every unavailable rank arm matches control exactly in terminal/action/state fields;
4. every available rank arm makes exactly one intervention and changes the action hash;
5. at least 224/256 tasks reach a root and at least 400 noncontrol arms are available;
6. each rank is available in at least 64 tasks, both seats and all eight opponents have an
   available arm, and at least two contested action planes occur; and
7. runner tests prove exact control and the one-decision budget.

Integrity failure quarantines value and permits only a defect repair. Support failure closes this
top-four contested vocabulary without reading terminal value.

## Frozen safe oracle and gates

For each task, admit control and each available rank arm that creates a crop and finishes with at
least `max(2, control_workers - 1)` own workers. Select maximum terminal margin, breaking ties in
favor of control and then lower rank. This is a descriptive teacher upper bound only.

Require all:

1. mean oracle margin gain over control at least +10;
2. strict improvement in at least 50% of rooted tasks;
3. mean own-score delta nonnegative or mean opponent-score delta nonpositive;
4. all eight opponent-family mean gains positive and the worst at least +3;
5. at least two distinct noncontrol ranks are selected strictly, each in at least eight tasks;
6. oracle crop creation is 100% and oracle worker-three reach is no more than five percentage
   points below control; and
7. control is available in every task and no safe task lacks an admissible arm.

## Decision rule

- **All gates pass:** retain the one-boundary concrete vocabulary and open D82, a bounded
  Monte-Carlo/value-controller approximation on fresh maps. No D81 arm itself is selectable.
- **Headroom failure with full support:** close top-four contested action search; spatial
  commitment may predict behavior without supplying a valuable response action.
- **Support failure:** close this root/vocabulary without value inspection or threshold expansion.
- **Integrity failure:** quarantine value and repair only the defect before an unchanged repeat.

No D81 outcome authorizes TestSession, submission, resident replacement, or Arena activity.
