# Swap R-1 G-1 reproduction and remedy ruling

Verdict: **PACKAGE_REPRODUCED; G-1 BLOCKED; DO NOT BUILD THE PROPOSED COMBINED-BFS
CONJUNCT YET.**

I reproduced artifact commit `31a9bd7957fd48b6c251da80659b472439453cdb` in a detached
worktree:

```text
python3 claude_1/swap1/make_swap_candidate.py  -> rc 0
python3 claude_1/swap1/g1_controls.py          -> rc 0, 11/11 OK
python3 claude_1/swap1/g1_sweep.py             -> rc 1, G-1 re-swap gate failed
```

The reproduced totals match the handoff: 52 fires / 12,981 unit-turns (0.401%), exact probe
parity and shadow inertness, 18 whole-game-identical zero-fire fixtures, and 111 repeated
unordered swaps within four ticks (OSC-006 98, OSC-011 13). OSC-027 has zero fires. No G-2
verdict was run or inferred.

## Remedy ruling

The reported progress idea is directionally right but is not yet a construction. At the
transport seam the mover's target is visible, but a stationary partner's planner target is not.
For a CHOP partner the only seam-visible action target is its current cell. A strict sum of the
pair's BFS distances therefore charges the mandatory one-cell displacement against the mover's
one-cell gain and can reject the intended OSC-005/027 pass along with OSC-006. It must not be
built on the assertion that it leaves the working yield cases untouched.

Before G-1 rev 2, extend the existing probe only (no candidate change) with a compact event table
for every fire in OSC-005, 006, 011, 012, 027 and 001 containing:

- mover id/current/landing/final target and the next cell from landing toward that target;
- partner id/current command and whether it was WAIT;
- whether the mover would vacate the partner's old cell on the following plan step;
- for WAIT partners, whether the next base tick gives that partner a non-WAIT command and its
  target, if observable from the already-run base trace;
- the reverse-swap tick or `none`.

Then propose the smallest stateless predicate that separates the two repeated-pair fixtures from
005/012/001. The first predicate to test is **pass-through viability**: for a working partner,
the mover must have a target beyond the occupied cell and its next step from that cell must vacate
it rather than stay or return. Do not claim this closes OSC-011: WAIT is only a command for one
tick, not proof that the partner is stably idle. If OSC-011 cannot be separated from OSC-012/001
with seam-visible facts, report that fact and propose the minimum explicit seam-input widening;
do not substitute a cooldown.

This diagnostic is authorized inside the existing probe and scripts. Candidate edits remain
blocked until the event table and revised predicate return for ruling. A seam-input widening is
a declared charter exception and needs the coordinator/owner to approve it before build.

## G-2 grading ruling

G-2 remains fail-first behind a green G-1. OSC-027 may be listed as **NOT REPRODUCIBLE ON THE
CURRENT BASE RERUN** if the base grader confirms that its chartered stall is absent; it must not
be counted FIXED or used to fail an otherwise correct cure for having no opportunity to fire.
The other three required cases remain 005/012/001, with every changed verdict listed. The
"partner back on work within two ticks" expectation remains untested, not passed, until there is
a clean non-dance working-partner fire.

## DEFERRED: swap R-1 G-1 rev 2 and G-2 through G-4

Postponed: candidate rev 2, G-1 rerun, fixture grading, panel, and Arena. Reason: the accepted
construction created a measured swap dance and the proposed remedy is under-specified at the
transport seam. Unblock: publish the probe-only event table and revised predicate; codex_1 rules
on the construction; if widening is required, coordinator/owner approves it. G-4 still requires
the owner's explicit go and remains controller-only.
