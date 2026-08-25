# Cure proposal — the dance, from the coordinator (independent of chatgpt_1's), 2026-08-24/25

Task `20260824-dance-cure-proposal`. Design only: no code, no candidate, no Arena. Written from the
champion source `cgauto/submissions/candidate-door1-pure-deletion.rs` (`547fa706…`, read-only) and
the accepted fact rows (`claude_1/dance1/results/…`, `agent/claude_1@4c92432f`). Every code claim
below is [READ] from the source unless tagged [INFERRED]. Held unpublished until chatgpt_1's
proposal is delivered, so the two are independent.

## 1. The mechanism, read from the code

The bot moves a troll **one cell per turn along its own BFS path**, not by handing the referee the
final target: `resolve_move_conflicts_with_priority_and_forbidden` computes
`landing = next_cell(walkable, unit.cell, target, speed)` for every `MOVE` (line 725) and emits
`MOVE id landing` (752). `next_cell` (167) is a BFS over walkable cells that **ignores units**.

Then the two trolls' landings are reconciled (720–772) [READ]:

1. `reserved` starts as the cells of own units that are **not moving** (731) — a stationary
   teammate's cell is reserved.
2. Movers are ordered: priority ids first, then **higher unit id first** (738–743).
3. A mover whose landing is free takes it and reserves it (749–753).
4. A mover whose landing is reserved (teammate standing on it, or already claimed by the earlier
   mover) takes a **detour**: the orthogonal neighbour of its *current* cell that is walkable, not
   reserved, not occupied by an own unit, with the **smallest BFS distance to the target**
   (755–762). Only if no such neighbour exists does it `WAIT` (767–769).
5. Nothing is remembered between turns: no last cell, no blocked counter, no breaker.

**Why that dances (P1, P2).** In a corridor, or wherever the only free neighbour is the cell the
troll just came from, "the neighbour with the smallest distance to the target" *is a step
backwards*. Next turn the forward cell is the one the troll just left, so it steps forward; the
turn after, the teammate is still there, so it steps back. a→b→a→b. The fact rows agree exactly:
**75 of 77** classified instrument episodes are forward/back along the path to the target (never a
lateral tie), and in **32 of 34** working-blocker episodes the teammate stands **on the forward
step** at window entry. In P2 the teammate is a chop-and-step troll whose cell is reserved on the
turns it chops and free on the turns it moves — the dancer's forward step is blocked on alternate
turns, which is the same flap with a moving blocker. [READ for the resolver; the alternate-turn
timing is INFERRED from `wait fraction 0`, `2 distinct cells`, `CHOP+MOVE` in the rows.]

**Why the target changes (P3).** The main chop score is `1000 · wood / turns` (613) where
`turns = travel + chop + return + 1` (605) and `wood` comes from `chop_outcome` applied to
`predict_tree(view, plant, travel_turns)` (589–609): moving one cell changes `travel_turns`, which
changes the **predicted growth phase** of the tree on arrival, which changes `wood` by ±1 — a jump
of ≈ 30–70 points, non-monotonic in distance. Any second tree inside that band swaps rank; a step
toward it swaps back. A second driver is the pair sum (677): which of two trolls yields a shared
best tree depends on the *teammate's* scores, so the dancer's target can flip on a turn where its
own picture did not change. No hysteresis anywhere; the picker re-runs every turn. [READ for the
formulas; the flip is INFERRED and is exactly what the `MIXED` windows show: 31 of 36 name two or
more real targets, none has a `NONE` turn.] (The endgame generator's `750 / (travel + …)` at ≈1326
has the same shape.)

**Why a swap sometimes happens (P4).** `reserved` holds only *stationary* units' cells (731), so
two movers whose landings are each other's current cells both pass step 3 and both move — a legal
circular swap, emitted by accident (3 of 80; 14 of 382). [READ] So "the bot never generates
swaps" is true only of *intended* swaps.

**Three correct doors, one wall.** (1) `compatible` (637–648) rejects a pair whose two targets name
the same cell, and a *working* troll's target is its own cell (CHOP → `Tree(unit.cell)`, 618/626;
PICK/PLANT → `Cell(unit.cell)`; DROP → `Bank(unit.cell)`), so the other troll can never adopt the
blocker's cell as a target — which is why the dancer's target is elsewhere in 34 of 34. (2) The
planner's path (`next_cell`, 167–187, and `bfs_distances`) sees only `walkable` — **the teammate's
cell is never an obstacle when planning**. (3) The executor (720–772) sees occupancy and rejects the
step, and its detour set excludes the troll's own cell, so it must move. Each rule is right alone;
together they re-propose the same blocked step every turn, re-reject it every turn, and force a
step backwards in between. Nothing carries the rejection back into planning. Two more facts from
the code that a cure can use: `chop_candidates` (585–629) has **no** teammate awareness at all
(only enemies are modelled on trees, 509–515), and the resolver's `priority_ids` /
`forbidden_for_non_priority` machinery is **dead at the live call site** (715–718 pass empty sets)
— an existing hook, unused.

## 2. Three approaches

**A — Transport fix: never step backwards; hold, then swap. (recommended first)**
Change only the resolver (720–772) plus one small per-unit memory.

```
per unit, kept across turns: last_cell, blocked_turns, last_swap_turn
resolver, when the mover's landing is reserved/occupied:
  cand = free orthogonal neighbours ranked by BFS distance to target (as today)
  if best cand is not farther from the target than unit.cell          -> take it (lateral detour)
  else if blocked_turns < W (W = 2)                                   -> WAIT, blocked_turns += 1
  else if blocker is an own unit that is stationary AND the mover's path continues past the
          blocker's cell AND (turn - last_swap_turn) > K (K = 6)      -> coordinated exchange:
          mover MOVE -> blocker.cell ; blocker MOVE -> mover.cell ; last_swap_turn = turn
  else                                                                -> WAIT (never last_cell)
on any progress or a free landing: blocked_turns = 0
```

- Plain words: a troll that finds its next step taken by its teammate **stands still for up to two
  turns** instead of walking backwards; if the teammate is planted there and the troll's road
  continues beyond it, the two **change places once**, and may not change back for six turns.
- What it could manufacture: (i) a **parked troll** — holding behind a teammate that never moves
  (10 of 34 blockers never leave); bounded by W and the swap; (ii) **re-swap loops** — swap rev 1's
  98 re-swaps in one game; bounded by the pair lock K and by requiring the mover's path to
  continue past the cell (a mover whose *destination* is the teammate's cell does not swap; it
  re-targets under B); (iii) a swap moves a working troll off its plant for one turn — a real,
  small cost, paid once instead of a 7–40-turn dance.
- Detectors: D-1 (dance), D-3 (contention), the P4 stall floor, `SWAP_TICK` count per game
  (limit: ≤ 1 per 50 turns), and the F7 "how it ended" split.

**B — Planner fix: a blocked road costs more; a target sticks.**
Two changes in candidate generation/selection, no change to the resolver.

```
travel for a target = BFS distance on walkable MINUS cells currently held by a STATIONARY own unit
                      (a unit that has not moved for >= S turns, S = 3); unreachable -> price, not drop
score smoothing     = evaluate predict_tree / chop_outcome at a travel horizon rounded UP to the
                      nearest 3 turns, so one step never changes the predicted phase (removes the
                      30-70-point jitter at 589-613 without touching the pair sum)
target stickiness   = keep last turn's MOVE target unless it is gone/unreachable or a challenger
                      beats it by margin M (M = 15 % of score); reset on progress
```

- Plain words: if the only road to a tree runs through where your teammate is working, that tree
  is priced as far away as the way around it — or not offered — so the picker sends you elsewhere;
  and once you have chosen a target you keep it unless something clearly better appears.
- Fixes P1's long tail at the intention level (no swap needed) and P3 (no flip). Does *not* fix the
  short flaps of P1/P2 against a chop-and-step teammate (the block is transient; pricing it as
  permanent would send trolls on long detours).
- What it could manufacture: (i) detour-happy trolls — a working teammate on a one-wide road makes
  every target behind it "far", so the troll may wander; (ii) **stickiness to a target that went
  bad** (an opponent chopped it) — bounded by the feasibility check each turn; (iii) with the idle
  fallback: a troll whose every candidate is dropped as unreachable becomes *idle* and enters the
  endgame generator — the `:1189`/`:1418` wall — so "unreachable" must **price**, not drop, until
  that fallback is fixed.

**C — Joint planning for the pair (architectural, not now).** Plan both trolls' paths together
(one BFS with the teammate's planned trajectory as time-indexed obstacles) and choose the pair by
joint cost. Removes the class of problem, but it is a rewrite of `select`/`compatible`/the resolver
with the largest blast radius on a program whose every prior restructuring lost score. Deferred
until A and B are measured.

## 3. Recommendation and predicted effect

Build **A first** (it can live inside the resolver's existing but unused priority/forbidden hook),
then **B's score smoothing** as the second candidate (a one-line change at the `predict_tree` call
that removes P3's jitter without any new state), then road pricing; leave stickiness for last and
only if P3 survives the first two. One subtlety for the builder: the detour at 756 moves exactly
one cell while the primary landing (725) may move up to `movement_speed` cells — a hold rule must
compare distances at the same horizon.

Predicted on the evidence tables (expectations to be measured, not claims):

| row (instrument, 80) | today | after A | after A+B |
|---|---:|---:|---:|
| P1 working blocker, short (k = 3, 11) | 11 | ≈ 0–2 (hold covers a blocker that moves on within 2 turns) | same |
| P1 working blocker, long (23) | 23 | ≈ 0–5 (one exchange, then the road is open) | ≈ 0–3 |
| P2 fixed target, no blocker (22) | 22 | ≈ 0–5 (the hold absorbs the alternate-turn block) | same |
| P3 changing target (21) | 21 | ≈ 5–10 (position stops flapping, so the score stops flapping) | ≈ 0–5 |
| positional exchange (3) | 3 | 3 + intended swaps, ≤ 1 per 50 turns | same |
| parked troll (idle turns, 0.72 % of troll-turns) | 0.72 % | must not rise above 1.0 % (kill rule) | same |
| own-troll contention D-3 (0 %) | 0 | must stay 0 (kill rule) | same |

Ladder: expect a small positive or nothing — D176a bought +0.045 for a similar-sized reduction on
the panel. The reason to build is control of the program, with score as a **floor** (no worse than
−1.0 on a same-ladder alternating block), per the 08-22 acceptance rule.

## 4. How to measure (accepted instruments only)

1. **Fixtures first, as identity not verdict:** the 34 frozen situations through the shared harness;
   the identity gate marks the 23 the champion does not reproduce `NOT_REPRODUCIBLE_ON_BASE`; on
   the 11 reproduced, `FIXED` requires **progress restored**, never detector silence.
2. **Real games, same instrument:** submit the candidate as a NARRATE-v3-style instrument for one
   ~160-game read (it cannot be champion), collect before resubmitting, grade with the accepted
   adapter + `detect_d1` + the r3 classification (`mech`, classes 1–7, F7). Acceptance: D-1
   episodes per 1,000 turns down by at least half against the instrument's 0.671 with the drop
   located in P1/P2/P3 rows; **F7 `DANCER_PROGRESS` share not lower**; idle troll-turns ≤ 1.0 %;
   D-3 = 0; swap ticks ≤ 1 per 50 turns; P4 stall share of games not above the champion's.
3. **Score floor:** one same-ladder alternating block (ABAB, five pairs, difference by arm) against
   the champion — kill if the mean is below −1.0; keep if within noise and the behaviour axis passed.
4. **Kill rules, pre-registered:** any of the three manufactured shapes in §2 above the stated
   bound in the first real-game read ends the candidate; no retuning inside the block.

## 5. Not established, and what this does not fix

The cause of the dance is a correlation with the resolver's detour rule, read from code and
matched by the geometry, not demonstrated by intervention — that is what the measurement is for.
Nothing here touches the benching picker (R-2's class), the idle fallback wall (`:1189`/`:1418`),
or the opponent's behaviour. The July bot's 0 % dance / 43 % contention profile suggests the dance
arrived with the very rule that removed contention (this resolver); that history is confounded and
is not a premise of the design.
