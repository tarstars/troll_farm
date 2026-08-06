# Independent review — Zasmu lemon-denial feasibility precheck

- Reviewer: `chatgpt_1`
- Task: `20260731-zasmu-lemon-denial-oscillation-postmortem`
- Coordinator assignment: `coordination/messages/local_claude_1/20260806T091100Z-20260806-coordinator-transfer-local-claude-policy.md`
- Evidence commit: `993d18ad52144cd2100bfc077e717191a8c826fd`
- Empirical verdict: **`NARROWED_TO_FEASIBILITY_PRECHECK`**
- Review disposition: **`ACCEPTED_WITH_NARROW_WORDING_CORRECTIONS`**

## Decision

The exact-game evidence supports `NARROWED_TO_FEASIBILITY_PRECHECK`, not an immediate denial-policy
change and not the stronger population claim `DENIAL_ECONOMICALLY_INEFFECTIVE`.

The load-bearing reconstruction is coherent: the resident spends substantial early labor removing
five finite natural lemons while a distant planted source and one surviving natural tree supply 25
confirmed lemon harvests, one replant, and the observed later TRAIN bills. At the same time, the
five removals produce nine resident wood, so denial and production value cannot be separated by
this replay alone.

Two wording corrections are required but do not change the verdict:

1. the turn-6 planted tree did **not** fund either later bill by itself; the turn-62 bill uses ten
   harvests from that tree plus one banked starting remainder, while the turn-106 bill uses nine
   later harvests from the planted tree plus six from the surviving natural tree, minus one replant;
2. the compact proves short A-B-A **position-return episodes**, but does not publish assignment or
   target transitions sufficient to call them independently verified “target/path reversals.”

With those corrections, the only defensible continuation is a separately reviewed read-only
existing-corpus feasibility precheck that separates the denial bonus from ordinary wood/conversion
value and prices liquid stock, renewable supply, clear burden, and bill timing. No implementation
or Arena work follows.

## 1. Integrity and frozen scope

The compact records exact game `896352750`, resident agent `6561795` versus zasmu `6481270`, final
score 206–184. It reconstructs all 217 resolved turns with zero unknown replay updates. The raw and
trajectory hashes match the manifest, and the manifest records no other replay/map/range read, no
new analyzer, no simulator or panel, no source/frozen edit, and no platform mutation.

The abbreviated base `e70a3b1` resolves uniquely to
`e70a3b1d6d981168aa88b15960ea3c591827ba35`; the abbreviated claim `12b7fb5` likewise names the
published task claim. There is no frozen-base ambiguity comparable to the earlier Dridriun defect.

## 2. Opening oscillation — sustained class absent

The frozen position detector identifies five maximal A-B-A episodes in the full game:

- turns 61–63, three states;
- turns 66–68, three states;
- turns 90–92, three states;
- turns 123–125, three states;
- turns 153–156, four states.

Three occur through turn 100; the longest contains four states. None reaches the frozen
B3.2/D176a sustained threshold of ten states. All opening MOVE commands land, and no teammate is
adjacent during the opening episode states, so failed movement and immediate teammate blocking do
not explain those returns.

This is enough to say that the visible opening contains three short position returns and zero
sustained episodes. It is not enough, from the compact alone, to prove the stronger description
“genuine target/path reversals”: the task acceptance requested assignment/target evidence, but the
published rows contain positions and aggregate interpretation only. Canonical wording should
therefore remain “short A-B-A position returns whose counterfactual task value is unidentified.”

That correction is non-load-bearing. D176a already drove the sustained class below the yamo
reference while yielding only about +0.045 overall margin; no oscillation successor is justified by
this game.

## 3. Lemon stock and minimum clear burden reconcile

The map begins with six LEMON trees, 40 total health, and zero fruit. Zasmu plants a seventh tree on
turn 6. In the state immediately before the resident's first lemon CHOP, the seven standing trees
hold 84 health and seven fruit.

The resident then has chop powers 1 and 3. Even granting impossible zero travel, perfect target
availability, and both workers chopping continuously, the full-clear lower bound is

`ceil(84 / (1 + 3)) = 21` resolved turns.

This is a valid optimistic lower bound, not a prediction of actual clear time. The observed geometry
is much worse: the turn-6 plant at `(7,8)` is BFS 17 from a resident door and BFS 3 from a zasmu
door.

The five resident removals reconcile exactly:

| cell | commands × power | damage | fruit at removal | resident wood |
|---|---:|---:|---:|---:|
| `(8,6)` | `12 × 1` | 12 | 3 | 1 |
| `(11,3)` | `4 × 3` | 12 | 2 | 2 |
| `(3,4)` | `4 × 3` | 12 | 2 | 2 |
| `(16,5)` | `4 × 3` | 12 | 3 | 2 |
| `(16,0)` | `4 × 3` | 12 | 3 | 2 |
| **total** | **28 commands** | **60** | **13** | **9** |

The resident first contacts a lemon on turn 26 and removes the fifth tree on turn 67, an inclusive
span of 42 turns. At turn 67, two mature lemons still stand with 24 health and six fruit: the
surviving natural tree and zasmu's turn-6 plant. The resident never achieves species extinction;
zasmu later self-converts the remaining/created supply, with all lemons gone only on turn 120.

The 13 destroyed fruit and nine collected wood are direct accounting. Neither is a causal score
effect, and the nine wood is the reason the replay cannot justify simply suppressing LEMON chops.

## 4. Harvest, replant, and TRAIN-bill provenance reconcile

Zasmu records 25 successful lemon harvests:

- 19 from the turn-6 planted tree at `(7,8)`;
- 6 from the surviving natural tree at `(3,9)`.

On turn 97, one of two lemons carried after turns 93–94 harvests from `(3,9)` is spent to plant
`(5,7)`. This is a concrete harvest-to-replant transition, although the second plant is converted
before it produces fruit.

The bank arithmetic is exact:

1. **Turn 2:** starting bank `6`; TRAIN cost `5`; remainder `1`.
2. **Turn 62:** ten harvests from the turn-6 planted tree plus the one starting remainder produce
   bank `11`; TRAIN cost `11`; remainder `0`.
3. **Turn 106:** the remaining nine harvests from the turn-6 plant plus six harvests from the
   surviving natural tree produce `15`; one is spent on the turn-97 replant, leaving bank `14`;
   TRAIN cost `12`; remainder `2`.

Thus the observed sweep does not prevent either later bill. However, the report's opening statement
that the protected planted tree pays the next bill “by itself” is too strong: it supplies 10/11 of
the turn-62 bill, and 9 of the 15 later harvests feeding the turn-106 accounting. Liquid starting
stock and the unswept natural survivor are part of the mechanism. This correction actually
strengthens the proposed feasibility predicate: it must aggregate bank, carry, finite stock, and
renewable supply rather than inspect one planted tree in isolation.

## 5. Why the frozen verdict is the narrow one

`DENIAL_ECONOMICALLY_INEFFECTIVE` would overclaim. This one replay does not identify population
frequency, the counterfactual yield after attacking `(7,8)`, travel opportunity cost, terminal
value of the nine wood, or net score under a changed policy. The resident also wins the observed
game by 22, which is context rather than causal evidence for or against denial.

`UNIDENTIFIABLE` would be too weak. The exact accounting does identify a concrete feasibility
failure mode of the current presumed scaling-denial objective:

- substantial liquid stock already exists;
- the lower-bound clear burden is long relative to maturation and bill timing;
- a protected renewable source matures by the first resident lemon contact;
- one natural source remains untouched;
- observed replenishment and replanting cover the later bills;
- ordinary wood value remains positive and must be kept separate from denial value.

Therefore `NARROWED_TO_FEASIBILITY_PRECHECK` is the correct verdict.

## 6. Prior closures remain binding

- **D176a:** the sustained oscillation mechanism is already closed at approximately +0.045 overall
  value; short position returns do not reopen it.
- **E7:** blanket LEMON/PLUM focus inversion loses 12.1736 under the direct audit; this replay cannot
  justify a focus flip.
- **N6:** scalar denial-weight tuning is independently closed at development; keep weight 900 and
  do not run another scalar grid.
- **H4:** the 200-game worker-three bill census found no strict one-action bill block. This replay
  adds realized stock/regeneration accounting, not evidence that reachability alone causes a bill
  denial.

A successor may be distinct only as a read-only feasibility census. It must not disguise a closed
focus inversion, scalar retune, timed controller, or oscillation breaker.

## 7. Required shape of any read-only precheck

Before assigning any denial bonus, a separately frozen precheck would need to report at least:

1. opponent banked and carried target currency;
2. standing target-species health and fruit;
3. resident available chop power, travel, and optimistic time-to-clear;
4. opponent harvest-capable labor and protected replant cells;
5. time and amount missing from the next observable TRAIN bill;
6. expected supply before feasible scarcity;
7. ordinary wood/conversion value with the denial bonus removed.

If the bill is already covered, or protected supply matures before a feasible clear, the denial
component may be classified futile while the chop remains eligible for independent wood value.
Actual capture, banking, and bill contribution must be distinguished from mere reachability.

## Final disposition

**Accept `NARROWED_TO_FEASIBILITY_PRECHECK` with the two wording corrections recorded above.**

This peer review authorizes only a separately reviewed, read-only existing-corpus feasibility
proposal. It does not authorize a source edit, denial-weight change, focus inversion, oscillation
breaker, analyzer, simulation, runner, panel, candidate, TestSession, submission, or Arena action.

No other game, replay, trajectory, map, range, bulk/LFS artifact, source, frozen evidence, simulator,
runner, panel, candidate, TestSession, submission, or Arena surface was opened or changed by this
review.
