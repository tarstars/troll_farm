# Banana restoration R2 successor host review

Date: 2026-08-05

Task: `20260802-banana-restoration-r2`

Candidate: `candidate-banana-r2.min.rs`, 76,386 bytes, SHA-256
`280ed777134a7f40783d759d0d327c1e70dece80680fc246675bc0a3c9eae9e6`, from remote commit
`85c68ee45333f373b95cd836408350f397fbc6b0` on
`agent/claude_1-banana-restoration-r2`.

## Verdict

**IMPLEMENTATION_INVALID pending a new revision.** The successor materially repairs all three
failures in the first handoff: the one-seed/surplus-bank regression is now non-vacuous and green,
the ownership-loss state has convert and abandon branches, and the branch contains a complete
compilable readable source. Two acceptance contradictions remain in the exact successor bytes,
so host replay/value gates and Arena publication do not start.

This verdict is about exact SHA `280ed777...`, not the value of the bounded banana algorithm.
No Arena or TestSession mutation occurred.

## Checks independently reproduced

- The exact remote candidate SHA is `280ed777...`.
- Optimized standalone compilation succeeds without warning suppression.
- The unchanged R-1 one-seed/surplus regression passes with zero violations.
- R-2a dynamic ownership-loss abandon passes with zero violations.
- R-2b dynamic ownership-loss convert passes with zero violations.
- The three compliant controls pass.
- Detector self-tests pass 23/23.

These results confirm that the retry fixes the first handoff's reported defects. They do not cover
the two cases below.

## Terminal failure 1 — conversion time ignores growth during chopping

The new ownership-loss branch decides conversion with:

`chop_turns = ceil(current_health / chop_power)`.

That is not the game transition used elsewhere in the same source. After each non-terminal chop,
the tree cooldown advances; when it reaches zero, a size-below-four tree grows and gains banana
health. The existing `MoisanBot::chop_outcome` correctly simulates this growth. The new branch
bypasses it, so it can claim that conversion finishes strictly before the opponent when it does
not.

A minimal boundary is an on-tree resident with chop power 1 against a size-2 banana at health 4,
cooldown 1, while the opponent ETA is 5. The new arithmetic reports 4 chop turns and accepts
`4 < 5`. Exact transitions require 5 chops: after the first chop, cooldown reaches zero, the tree
grows to size 3, and gains one health. Conversion therefore does not complete strictly before the
opponent ETA. The committed t4 regression uses a long cooldown and cannot expose this branch.

The revision must use an exact growth-aware prediction through both resident travel and chopping
(the existing `predict_tree`/`chop_outcome` mechanics may be reused where their opponent model is
appropriate) and add this near-growth boundary as a red-on-`280ed777...`, green-on-successor test.

## Terminal failure 2 — D-8 and I-10a remain contradictory and the test is vacuous

I-10a requires conversion of a lost mother when conversion is feasible. I-14 and D-8 still state
that an own-planted diagonal mother is never chopped, with zero exceptions. The committed t4
convert scenario begins with a pre-existing mother, so `own_banana_history` does not classify it
as our plant. D-8 therefore passes without testing the conflicting case; the handoff explicitly
acknowledges this.

Integrator ruling: **I-10a ownership-loss conversion overrides diagonal-mother protection only
after the mother has actually flipped to lost.** This follows the owner's resource rule: do not
leave fruit for the opponent; if exact conversion wins the race, turn the lost asset into wood.
I-14/D-8 continue to forbid every discretionary chop while the mother remains owned.

The revision must amend every affected invariant and the D-8 detector, add a non-vacuous trace in
which our resident plants the diagonal mother and a later opponent move flips ownership, and show
that exact feasible conversion passes both I-10a and the revised D-8. A negative control must still
make discretionary chopping of an owned diagonal mother fail D-8.

## Required disposition

Do not submit, value-test, or run the remaining host replay gates on exact SHA `280ed777...`.
A successor needs a new source hash and handoff, exact growth-aware conversion arithmetic, a
red/green near-growth regression, the ruled D-8/I-10a specification and detector amendment, and a
non-vacuous own-planted ownership-flip conversion trace. The earlier one-seed, abandon, readable
source, equality, and detector gates remain mandatory and must stay green.
