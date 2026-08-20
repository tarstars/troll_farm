# Pair-selector Phase 2 unified review — 2026-08-20

Verdict: **PACKAGE_REPRODUCED; BOTH CANDIDATES BLOCKED AS QUALIFIED CURES.** The dual-base
package at corrected artifact commit `14b575ce00542598c465046746b7fc14c531d9bf` is coherent,
honestly reports its limitations, and satisfies the card as a ready-with-gates delivery. It does
not qualify either candidate for promotion or support calling P1+P2 a situation cure.

## Independent execution

From a detached worktree at the original package commit `5409ba13c04d87f81dbad4b13138986da2942898`,
I ran `python3 claude_1/picker2/run_gates.py --skip-panels`. The rerun rebuilt both candidates
from allowlisted subjects, reproduced the byte-identical diff body and patched selection regions,
recompiled all four probes, reran the fail-first fixtures and all-34 sweeps, and independently
re-read the committed 240-game panels through the floor, decomposition, direction-control,
named-change, and process-parity checks. All non-panel steps passed. The four expensive panels
were not rerun; their committed keyed rows were consumed by the downstream checks.

The rerun reproduced:

- benched turns falling to zero on every fixture red on its own base, with P1 firing on every
  candidate arm;
- standing FIXED totals `3 -> 4` on cure-C and `8 -> 8` on door-1;
- blocking totals `53 -> 33` and `43 -> 35` on matched 240-game panels;
- de-novo/healed `0/20` and `0/8`, with swapped arms refilling the de-novo bucket with exactly
  the healed keys; and
- 8-process/1-process parity across 8,160 compared fields.

My single-draw latency rerun also changed the reported deltas, independently corroborating
Claude's correction: the timer resolves neither patch cost above host noise. The corrected claim
is only that all observed p95 draws remain far below the 50 ms budget.

## Gate interpretation

The package's headline is right: removing a selector-level bench is not the same as restoring
progress. On cure-C, OSC-004/013/017 become detector-quiet while `progress_restored` remains
false; only OSC-034 becomes FIXED. Door-1 adds no FIXED situation. Therefore both candidates are
**blocked as qualified cures** on the standing grader.

The new P3 on door-1 `m004` is not an open reviewer ruling. The locked panel configuration says
P3 is an absolute candidate-equals-parent orchard-inertness requirement and explicitly records
that it was kept. An intentional selector edit does not silently make that invariant
inapplicable. Door-1 therefore has a named absolute regression unless the owner explicitly
changes the rule. Both bases also add P4 plus `r5-horizon` on `m021` inside an already-blocked
game. A zero de-novo *game-block* count does not erase a new property violation hidden inside a
game already blocked for another reason.

This is not a request to revise the evidence package: it names both costs correctly. It is the
review verdict on what that evidence licenses. The two artifacts may remain on the shelf for the
owner's D3 choice, but neither is a qualified cure and neither authorizes Arena action.
