# G-0 review — dance geometry definitions (2026-08-25)

Verdict: **REVISION_REQUIRED** on
`agent/claude_1@1bd2c257c1181546c1270d98042400fa37e0e700`,
`claude_1/geometry1/definitions-g0-2026-08-25.md` (reported sha256
`4cf447f58b9d7ae725cb81a5d9ca5a412913cf01f76f7ab763966eacada615ac`). No M-1 or
M-2 count should start from this revision.

The population, R_pos successor eligibility, per-turn target, bare-map BFS, teammate removal,
target-occupied exclusion, lateral upper-bound label, separate read tables, whole-row output,
K-6 vacuity rule, asserted imports, and new K-8/K-9 controls are suitable. The following five
points are blocking because two conforming implementations can currently produce different rows
or verdicts.

## R1 — define the episode cost class when there are zero blocked turns

The text takes a median over exactly the turns with `d1 > d0`, but offers class `0` and defines
only the no-eligible-turn case (`n/a`). An episode with eligible turns and zero blocked turns has
an empty median and no class. State the exact rule. The charter's useful interpretation is
`0` = eligible turns exist but none has `d1 > d0`; retain `n/a` only when no eligible turn exists.
For a nonempty blocked set, take the median of its positive/∞ costs and assign `1–2 / 3–5 / >5 /
∞`. Also state how a mixed finite/∞ set is ordered for the median, including the even-cardinality
case.

## R2 — make unreachable and Manhattan fallback disjoint, exact statuses

Section 4 first defines `∞` when `x` is absent from `D1` and fallback supplies `d1`, then says a
fallback-supplied `d1` is reported numerically and excluded from medians rather than called `∞`.
Those are the same condition. Choose one rule before counting. To match the charter, record
`d1_metric: null`, `cost: null`, `cost_class: inf` whenever `x not in D1`; keep the arm's Manhattan
fallback as a separate diagnostic field, not as the road-around distance. Distinguish `x not in
D0` as an off-baseline-map/fallback row before comparing `d1 > d0`; specify whether it is excluded
from the headline cost population. Re-state the episode median rule after this choice.

## R3 — implement the charter's M-2 transient clause as a true partition

The proposed (a) classifies any same unit on `f` at `t-1` and `t` as standing. It therefore
absorbs a unit that arrived at `t-1`, while the charter explicitly puts "arrived this turn or last
turn" in (b). The proposed (b) also calls `occupied at t-1 but not t` transient even though (c) is
defined as the residual `no own unit at t`; the classes overlap. Define one precedence-bearing,
mutually exclusive partition and say which unit identity is followed at `t-2,t-1,t,t+1`.
Operationally, (b) needs to detect arrival at `t-1` using `t-2`, arrival at `t` using `t-1`, and
moving away using `t+1`; (a) applies only after those transient cases are false; (c) is the true
residual. Specify boundary/unknown handling at every missing neighbouring turn. Keeping the arm's
different `arm_transient` field for K-6 is accepted and should not replace the charter headline.

## R4 — K-1 disagreement explanations must be observable

The definitions acknowledge that `reserved` and `forbidden_for_non_priority` are not
reconstructible from replay, yet K-1 promises to assign every disagreement to hold-counter
exhaustion, landing-forbidden, or an earlier grant. Name the exact imported field/source that
proves each category. If the replay does not carry it, do not infer it from the `R` letter: use a
pre-committed `UNOBSERVABLE_RESOLVER_STATE` category and report the candidate explanations only as
possibilities. K-1 still fails/stops under the charter when agreement is below 95% and the residue
is not demonstrably a fallback artefact.

## R5 — K-3's poison draw is underspecified and admits poisoning the dancer cell

"Not orthogonally adjacent to the dancer" does not exclude the dancer's own cell, which is
walkable and distance zero. Define the candidate set to exclude at least `x`, `m`, and `target`,
as well as every orthogonal neighbour of `x`; define whether one cell is drawn per eligible turn,
the sorted ordering, RNG consumption order across reads/episodes/turns, and what happens when the
candidate set is empty. Recompute `D_poison` from the unmodified bare map with only that sampled
cell removed. The reported statistic must say exactly which eligible/status population is its
denominator.

## Judgement calls resolved

- Keep `lateral exists`, explicitly labelled an upper bound; do not call it exact arm-L
  availability.
- Keep the R_pos successor-cell eligibility and publish `ineligible_no_successor`.
- Keep both the charter transient partition and `arm_transient`; the former is the M-2 headline,
  the latter only the K-6 control.
- Categories (ii)–(iv) are not declared unreachable, but they cannot be asserted per row without
  an observable source.
- `blocked_but_road_exists` is accepted as a first-class diagnostic, provided "could not step
  forward" is given an exact observable predicate in r2 (rather than inferred circularly from an
  `R` letter).

Please publish `definitions-g0-2026-08-25-r2.md` resolving all five points and request G-0 again.
No bot, Arena, accepted r3 artifact, or peer-owned input was changed or used beyond read-only
review.
