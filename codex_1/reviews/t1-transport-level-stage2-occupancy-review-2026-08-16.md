# T-1 stage-2 occupancy review — 2026-08-16

Verdict: **STAGE-2 IMPLEMENTATION ACCEPTED AS A PARTIAL FEATURE.** Its 0/34 result is
descriptive only and does not grade the full T-1 prediction.

Reviewed artifact `9d99d62a11c55d53da04cd509e71cae57e801db6` independently:

- `check_invariants.py`: pass, including the naive-control failures;
- candidate compiles and re-runs all 34 fixtures;
- result reproduces 0 FIXED / 34;
- OSC-008 and OSC-012 alone become detector-quiet, both with progress false and thus
  correctly remain NOT_FIXED;
- resident digest remains `98628e98…` and the delivered diff leaves `compatible()`,
  WAIT's `Target::None`, and both protected branch conditions untouched.

The option-B wiring is correctly located after candidate generation and door-unblocking,
so `idle_peer_cells` sees the final per-unit candidate lists used by `select`. Pair and
greedy selection both reject a spatial target held by a different idle unit; the mover's
own cell is exempt. The implementation does not confuse an idle peer's cell with the
mover's own held cell.

The invariant checker is honestly source-level, not runtime reachability. In this
increment that is sufficient to establish non-regression because the relevant marker
and branch conditions are unchanged and the source diff is confined to occupancy-map
construction and selection filtering. A later rewrite of candidate generation would
need runtime branch coverage rather than inheriting this result.

Boundaries retained:

- no claim that visibility alone satisfies any of the 25 full-feature predictions;
- quiet-but-stalled remains NOT_FIXED;
- the stage-1c target-reached-versus-progress-only contract question remains open before
  final prediction grading;
- idle-yield and atomic swap require their own implementation reviews.
