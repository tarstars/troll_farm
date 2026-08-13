# D-1 has two duration modes, and the terminal one never occurs against an aggressive opponent

- Date: 2026-08-08
- Author: `local_claude_1` (Phase 1 item 9)
- Read-only. No detector, bot, gate, or Arena change. No games run.
- Input: `local_claude_1/verification/local_claude_1-floor-selftest-result-2026-08-07.json`
  (240-game parent-vs-parent floor, parent `a8eb3b2b`)
- Builds on: `claude_1/banana-restoration-r2/feasibility-raw-zero-2026-08-07.md`, which
  root-caused D-1 into D1-A (34/35) and D1-B (1/35). **That analysis is not superseded** — this
  is an orthogonal cut of the same 35 episodes.
- Status: **PROPOSED finding.** Reviewers per allocation: `claude_1` (execution),
  `chatgpt_1` (adversarial).

## What is new here

`claude_1` established the *mechanism* of D-1: D1-A is same-tree contention against a memoryless
detour tie-break, localised to
`MoisanBot::resolve_move_conflicts_with_priority_and_forbidden` (`yamo_orchard_live.rs:1503–1519`),
with resolver replay reproducing 34/35 episodes turn-by-turn and **34/34 having a parked
adjacent peer**.

This adds the *conditions under which that mechanism becomes terminal*, which the mechanism
analysis does not give — and which is what a fix must be judged against.

## Measured: the 35 episodes are sharply bimodal

| mode | episodes | duration | distinct games | runs to game end |
|---|---:|---|---:|---:|
| SHORT | 15 | 6–34 turns | 12 | 0 |
| LONG | 20 | 62–194 turns | 13 | 15 / 20 |

There is almost nothing between: the gap runs from 34 to 62 turns. The longest episode occupies
**194 turns of a 200-turn game** — a unit alternating between two adjacent cells, with zero
progress events, for 97% of the game. Every episode in both modes is between orthogonally
adjacent cells.

## Measured: the terminal mode never occurs against an aggressive opponent

Counting **distinct games**, not episodes (episodes cluster within games, and counting them
would inflate this threefold):

| mode | games | idle | harvester | chopper_aggressor |
|---|---:|---:|---:|---:|
| LONG | 13 | 5 | 8 | **0** |
| SHORT | 12 | 2 | 4 | **6** |

`chopper_aggressor` is 30.0% of the floor panel (72/240). Observing **zero** in 13 LONG games
has p ≈ 0.0097 under that share. Three games contain both modes, so the two sets are not
disjoint.

**Correction of my own working figure:** I first computed this over 20 episodes and got
p ≈ 0.0008. Those 20 episodes come from only 13 games, so the episode-level figure overstates
the evidence by treating repeats within a game as independent. The game-level p ≈ 0.0097 is the
honest number, and it is the one to cite.

## Interpretation — hypothesis, not measurement

D1-A requires a **parked adjacent peer**. A parked peer is a persistent condition, and it
should persist longer when the world is quiet. An aggressive chopper keeps changing the board —
felling trees, taking targets — which retargets our units and dissolves the parked-peer
condition before the bounce can become terminal. Against idle or harvester opponents nothing
perturbs the tie, so the detour bounces until the game ends.

This is consistent with, and mechanistically distinct from, the P4 calibration finding that the
resident "finishes the work the map offered and coasts to the horizon". **These are not the same
thing:** P4 coasting is the map being exhausted; D1-A is two of our own units deadlocked over a
tree that is still there. 30/34 D1-A episodes have the peer standing on a plant.

I have not tested the hypothesis. Testing it needs per-turn state from the LONG games, which is
Phase 2 work.

## Why this matters for a fix

It supplies a **falsifiable acceptance criterion** that the mechanism analysis alone does not:

> A correct D1-A fix must eliminate the LONG mode entirely — including all 15 episodes that run
> to game end — and should leave the SHORT mode largely intact, since the SHORT mode is where
> the opponent already breaks the tie for us.

A fix that halves the episode count but leaves terminal deadlocks is not a fix; it is the
D176a outcome, which passed its own gate perfectly and left the worst run unchanged at 247
turns. The mode split makes that failure detectable in advance.

It also connects D1-A to an existing owner ruling. The **Elost rule** — "a capable worker
already standing on a live tree owns that tree for the current decision; do not send a second
worker to the occupied cell" (exact game `897556967`) — describes precisely D1-A's
precondition. The rule was authored from a live incident, independently of this detector. That
convergence is worth weighing when choosing the guard.

## Standing tension the owner should see

Raw D-1 = 0 is owner-standing and non-negotiable, so Phase 2 must reach it for the **gate** to
pass. But oscillation's measured *value* is +0.045 margin, CI [−0.024, +0.114] — D176a reached
a 2.88% long-run rate, below yamo's own 2.9% reference, with all six value gates passing, and
was still not worth a promotion cycle.

So D-1 repair is a **gate-compliance requirement, not a score improvement.** That is a coherent
position — an instrument cannot certify a candidate while the reference deadlocks for 194 turns
— but it should be held deliberately rather than by inheritance, because the work buys
correctness, not rating.

## Boundaries

The mode split, the durations, the game counts and the profile mix are measured from the
committed floor artifact and reproduce from it. The causal story about parked peers persisting
under quiet opponents is a hypothesis. The Elost connection is a resemblance between an
owner-authored rule and a measured precondition, not evidence that the rule fixes D1-A.
