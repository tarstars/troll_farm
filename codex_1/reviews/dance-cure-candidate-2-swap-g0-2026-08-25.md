# Candidate 2 G-0 review — DESIGN_ACCEPTED

- Task: `20260825-dance-cure-candidate-2-swap`
- Reviewer: `codex_1`
- Reviewed UTC: 2026-08-25T16:56:07Z
- Artifact: `agent/claude_1@6eb89209961a67e22e80c8c807b38947868c990a`,
  `claude_1/cure2/definitions-g0-2026-08-25.md`
- Artifact SHA-256: `e5077bb411420d2c57a9be10c4e49d79aa58079d40138a541c3fe56e06b4e450`
- Scope: design and proof only; no Candidate 2 code existed at the reviewed commit.

## Ruling

**DESIGN_ACCEPTED.** The exact predicate and its proof discharge G-0. Implementation may begin,
subject to the frozen predicate, controls, bars, and reporting obligations in the reviewed file
including Addendum A. This ruling authorizes G-1 only. It authorizes no Arena action.

## Proof finding

Theorem 1 is sufficient for owner rule R-1a. After `SWAP_t(M,B)`, both units changed cells, so on
turn `t+1` neither can satisfy clause 4 as the standing partner. Consequently neither the reverse
orientation nor the same orientation can fire on the next tick, regardless of either target. The
prevention is the standing-worker predicate itself, not a timer, counter, lock, or new memory.

Theorem 2 correctly limits a later reverse exchange: `M` must first stand on `L` across a complete
transition and `B` must later acquire a target strictly beyond `L`. The rule writes no target, so
that later condition is a planner event. C-5 measures rather than prevents it, as the charter
requires.

One sentence in §4.3's explanatory paragraph is too strong: at a later earliest reversal,
`c_t'(B)` need not still equal `c_t(M)` because `B` may have moved during the intervening turns.
The theorem and corollary do not depend on that equality: clause 6 directly establishes
`d_T(L) < d_T(c_t'(B))`, and an unchanged target of `L` (or `None`) still cannot reverse. G-1 must
not repeat the equality as an invariant, and C-5 evidence must report both units' actual cells and
targets at each exchange. This is a reporting correction, not an open edge case or predicate
change.

## Judgement calls and construction constraints

1. Keep clause 5 as written: exclude non-adjacent landings and publish `sn=` and its blocked-turn
   share. Do not introduce a first-step fast-unit variant in G-1.
2. Keep clause 7 as written: decline an exchange when an earlier mover already holds `c`; preserve
   base mover order.
3. Keep R-B whole-game orchard scoping. Print the scope-inactive game/share beside every G-2
   headline; do not describe the result as a whole-corpus cure.
4. C-10 is 100% or stop. On a separately owner-authorized G-2 read, report C-10 on the first
   collected real game before reading aggregate results.
5. A positive C-5 is stop-and-ask, never a lock. Split it by the side whose target changed and
   include actual cells, targets, turns, and ids. A positive C-6 returns the design to G-0.
6. Preserve the remaining hard controls: alpha parity, single-pass `pz=1`, poison-arm bite,
   mutual v4/v5 refusal, fail-closed slot mapping, P3 red-half, P4b once accepted (otherwise the
   1.5% interim net), and every named cost/refusal count.

## Edge-case audit

E-1 through E-13 are closed for G-0. Multi-unit conflicts are bounded by `displaced` plus the two
granted cells; speed-2 and target-occupied cases are excluded with counters; unknown history and
slot mismatch fail closed; both granted cells inherit the dormant forbidden-cell guards; the hold
is off and Candidate 2 adds no holder, making the one-pass invariant testable; the displaced
partner's lost action is explicitly priced. No open proof edge case remains.

