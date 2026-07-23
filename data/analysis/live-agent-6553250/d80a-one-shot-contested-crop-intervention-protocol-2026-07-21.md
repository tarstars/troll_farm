# D80a one-shot contested-crop intervention — frozen protocol (2026-07-21)

## Question

D78 proves that current opponent-to-crop geometry carries held-opponent commitment signal. D79
proves that concrete spatial job choices have large safe whole-game headroom, but rejects an
unconstrained scorer because every random policy replaces every task trajectory. Does one sparse,
coefficient-free contested-crop intervention have prospective causal value over exact D40?

D80a changes the action interface and intervention budget; it is not a D79 rescale, population
repair, parameter search, learned selector, or candidate test.

## Frozen intervention

Keep exact D40 for TRAIN, deficit funding, shack evacuation, job persistence, provenance,
reservations, the shared PICK ledger, transaction revalidation, and every ordinary fallback.

At a D40 `Rate` boundary, compute the exact-prior candidate order and D42 job context. A candidate
is a **contested crop job** iff:

1. its action plane is `FELL_BANK`, `HARVEST_BANK`, or `RENEW`; and
2. its target has current opponent distance at most two (`job_context[13] == 1`).

The candidate policy may intervene only when exact-prior rank zero is not a contested crop job and
at least one of ranks one through three is. It chooses the lowest-rank such challenger. It may do
this at most once in the whole episode; after the intervention it executes exact D40 through
terminal. If no such boundary occurs, it is exactly D40. The control is exact D40 everywhere.

No target-health, fruit, distance, turn, score, workforce, opponent, or rank threshold beyond the
definition above may be added or changed after execution.

## Frozen execution

Use previously unopened official maps 9,910,000--9,910,015, both seats, and the unchanged eight
D40 opponents: 256 paired tasks and 512 rows per repeat. Execute the complete control/candidate
matrix twice with 20 threads; sort by `(policy, map_seed, seat, opponent)` and require byte
identity. Maps 9,911,000--9,911,031 are sealed from D80a.

Record exact D40 terminal/mechanics/action fields, action planes, reward identity, maximum workers,
eligible boundaries, interventions, challenger rank/plane, and finite/legal failures. Verify the
control directly chooses `teacher_index`; verify the candidate makes at most one intervention and
otherwise chooses the same action.

## Stage A: frozen integrity and activation gates

Open no paired score or outcome summary unless all hold:

1. complete byte-identical 2 x 256 repeats;
2. zero invalid command, provenance, deposit-prediction, worker-cap, reward, finite-feature, legal,
   fallback, or intervention-accounting failure;
3. every control/candidate nonintervention task has exact terminal/action/state parity;
4. candidate intervention and changed-action-hash task counts are identical;
5. at least 32 and at most 230 of 256 tasks intervene, and the changed-task rate is 10%--90%;
6. both seats and at least six opponent families contain an intervention; and
7. at least two challenger ranks and at least two crop-job action planes execute.

If Stage A fails, stop without opening value and close this sparse challenger definition.

## Stage B: frozen paired value and safety gates

Only after Stage A passes, summarize candidate minus control. Require all:

1. active-task mean margin delta at least +4 and map-cluster normal 95% lower bound above zero;
2. overall paired mean margin delta at least +1;
3. at least 55% of active tasks improve strictly and at most 35% regress;
4. active-task mean own-score delta at least -5 and opponent-score delta at most +2;
5. at least six of eight active opponent-family mean margin deltas are nonnegative and the worst
   is at least -15;
6. crop creation remains 100%, worker-three reach falls by at most five percentage points, and the
   candidate has no more than two additional catastrophic losses (margin <= -100); and
7. candidate negative-margin mass is at most 105% of control.

## Decision rule

- **Stage A failure:** close this one-shot contested top-four interface without threshold/rank
  expansion or reuse of these maps.
- **Stage A pass, Stage B failure:** retain the causal result but close the fixed intervention; the
  next discriminator may be a bounded rollout/value search over the same concrete challenger
  vocabulary on new maps, not a learned selector of failed labels.
- **Both stages pass:** freeze the sparse interface and open D81, a preregistered bounded
  multi-boundary/Monte-Carlo value controller on fresh maps. D80 itself remains a mechanism result,
  not a submission candidate.
- **Integrity failure:** quarantine outcome interpretation and repair only the defect before an
  unchanged repeat.

No branch opens D80 sealed maps, constructs a submission, calls TestSession, or touches Arena.
