# Cure alpha rev 2 G-1/G-2 reproduction and reviewer verdict

Task: `20260821-swap-r1-cure`

Reviewed handoff: `coordination/messages/claude_1/20260821T122510Z-20260821-swap-r1-cure-rev2-g1-g2-handoff.md`

Pinned artifact commit: `65c716b33c50f120143b035b2fb36969a2a148a5`

## Verdict

`PACKAGE_REPRODUCED; BLOCKED AT G-1.`

The amended population measurement is accepted as positive evidence: D-1 episodes are 27 -> 9
with healed-minus-new +18, and P4 violations are 16 -> 0 with healed-minus-new +16. It does not
advance the candidate past the fail-first gate because G-1's no-repeated-swap condition still
fails with 13 re-swaps, all in OSC-011. The construction ruling required measuring and reporting
that residual; it did not waive the gate. The only evidenced separation is the still
owner-blocked planner-target widening. Do not run G-3 or broaden the candidate under this verdict.

The narrowed P5 candidate also remains explicitly short of the owner-approved R-1 rule: it drops
the CHOP/HARVEST working-partner exchange. This scope cost travels with the positive population
result.

## Rulings on the two reviewer questions

1. The residual 13 block progression. G-1 is strict and fail-first. A positive G-2 population
   result cannot cure a failed G-1.
2. P3 remains applicable as a named regression signal, but this single alpha occurrence is not
   independently established harm. On this task's amended G-2, the growth is fully explained by
   alpha's intended exchange at m004 seat 0; the floor's zero column is vacuous because its
   candidate equals its parent. Therefore it is recorded, not treated as a second blocking fact.
   This does not create a general exemption and does not modify the anti-benching card's explicit,
   owner-upheld P3-clean requirement.

For the basket instrument, the handoff establishes that cure-arm episode identity is the wrong
question: changing the recorded window is the expected effect of a cure. A sound replacement is
to require identity only on the subject/base arm, then grade the candidate arm for absence of the
same detector/classifier shape over the corresponding game and named window with all changed
commands retained for inspection. That replacement is a proposal for the coordinator/owner, not
a unilateral gate amendment. OSC-005 remains a substantive miss regardless because alpha fires
after its recorded episode.

## Independent reproduction

In a detached worktree at the pinned commit:

- the rev-1 builder reproduced the candidate, probe, and control byte-for-byte;
- the rev-2 candidate SHA-256 reproduced as
  `575ccbd61ea90f506da47a70dd1b59e60196a83bd04812c58b0a7910ebeeef1f`;
- G-1 reproduced 25 fires over 12,981 unit-turns (0.193%), four checks passing and the
  repeated-pair check failing with 13 OSC-011 re-swaps;
- controls reproduced 11/11;
- both 240-game panels reproduced (candidate panel 26 blocking, floor 43 blocking);
- Gate M matched all 240 base arms byte-for-byte;
- regenerated `g2-panel-rev2-2026-08-21.json` had SHA-256
  `6acb979cf506b9d779ae70219b91378679b19170258ac2c622a1b952cc542344`, byte-identical to the
  committed artifact;
- baskets reproduced 11/34 base fixtures, no healed fixture, no lost FIXED fixture, OSC-005 still
  NOT_FIXED, and OSC-001/012 rejected by cure-arm identity after alpha changed their windows.

The panel runner's exit 1 is its expected legacy BLOCK verdict, not a reproduction failure.

## DEFERRED: planner-target widening / alpha replacement

Postponed pending an explicit owner/coordinator ruling on the charter exception and on whether the
programme should build a replacement alpha after this G-1 block. No widening or G-3 work is
authorized by this review.

## DEFERRED: anti-benching Phase 3b pre-build ruling

Postponed because no concrete Phase 3b design proposal was delivered. The owner-controlled
extend-versus-replace choice remains unanswered, and the proposal must still state the exact P1
fallback, beta/OSC-030 scope, OSC-010 parking, and task-specific P3 rule before review. No Phase 3
build is authorized.
