# Pair-selector Phase 1 mechanism review — 2026-08-20

Verdict: **PHASE_1_ACCEPTED**. The pinned mechanism evidence at
`8cacaa080bb7f8ca1a92de0704dde205fcfc64c1` answers the charter's WHY question and may go to
the owner's design gate. It does not authorize a fix build.

## Independent execution

I ran the delivered step-0 identity check, the probe over all 24 `GOAL_SPLIT_WRONG`
situations, and the deadlock check from a detached worktree at the pinned commit. The rerun
reproduced:

- exact identity of the three selection regions across the two night arms, while correctly
  limiting that result because the changed forecast hunk can alter candidate scores;
- 2,245 benched-with-work turns: 1,435 `SCORE_PREFERENCE` and 810
  `TIE_ENUMERATION_ORDER`;
- `INCOMPATIBLE_TARGET` at the winning partner candidate on 2,245/2,245 turns and no stock
  blocker; and
- 2,010/2,245 partner moves onto the benched troll's occupied cell, with the remaining 235
  moves going elsewhere.

The instrument satisfies the one-scoring-path requirement: it hoists the selector's own
`compatible` and `stock_compatible` results into logged bindings consumed by the original
branch. Command-stream parity against the uninstrumented subject and exact per-window turn
coverage run before classification. The tie mechanism follows from the strict `>` update and
enumeration order, and the observed 10/10 lower-id benching supplies the predicted consequence.

## Scope guard for the design gate

P1 is directly supported for the 2,010 self-defeating occupied-cell moves, including all four
owner-ruled cases. P2 directly addresses the 810 exact ties. Their overlap was not presented as
a union covering all 2,245 turns, and the handoff correctly leaves the 235 non-deadlock turns
out of scope. Therefore `P1 + P2` is an evidence-backed narrow proposal, not a claim of complete
R-2 compliance. Phase 2 still requires the owner's choice, a settled-resident rebase, fail-first
fixtures, and the chartered named-costs/platform gate.

No resident or Arena action occurred in this review.
