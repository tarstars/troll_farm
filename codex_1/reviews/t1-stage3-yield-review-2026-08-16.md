# T-1 Stage 3 idle-yield review — 2026-08-16

Verdict: **MEASUREMENT ACCEPTED; PROPOSED TWO-WAY DESIGN FORK REJECTED AS INCOMPLETE.**

Reviewed pinned artifact `853dc8b282149acf865097e82d940929c25dfdb9` and independently ran the
13-case harness self-test plus all 34 frozen situations. The committed JSON reproduced exactly:
0 FIXED / 34, with every Stage 3 result row byte-equivalent as parsed JSON to Stage 2. A stronger
control compiling both candidates and comparing their full command streams on every fixture also
found **zero differing command streams**. Thus idle-yield as implemented is behaviorally inert on
this library, not merely unchanged under the grader.

The handoff's explanation is directionally correct but overbroad. `apply_idle_yield()` marks only
the final destination encoded in another unit's `MOVE`; it never asks whether an idle peer holds
the mover's projected landing or a later route cell. That cannot detect the dominant route-blocker
shape represented by M1.

The claimed choice between “accept a path mirror” and “drop yield” is not exhaustive:

- the candidate already contains and uses its own `next_cell()` mirror in
  `resolve_move_conflicts_with_priority_and_forbidden()` and elsewhere;
- the referee engine computes `next_cell()` from static walkability before its separate
  same-player collision-resolution loop. Opponent simultaneous resolution is not an input to
  `next_cell()` itself;
- therefore reusing and parity-testing the candidate's existing projected-landing computation is
  a third available design. A later-route-cell feature would require a stronger path contract,
  but immediate landing detection does not require introducing a new mirror.

No ruling is made here to alter the charter or drop Stage 3; that is the coordinator/owner's
decision. Stage 4 can be evaluated independently. If Stage 3 is revised, first specify whether
its target is the next projected landing or any cell on a future route, then add a positive
fixture where the intended predicate fires and a negative fixture that distinguishes destination
from landing/path. Do not infer global unreachability from this 34-case library alone.

The Stage 3 result remains progress-only under the existing prediction-grading hold.
