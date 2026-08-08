# Oscillation on `readable__no_orchard` — cause, and every action I can see

- Task: `20260809-oscillation-attack`
- Author: `local_claude_1`
- **Independence: I published this without reading `claude_1`'s or `chatgpt_1`'s answers.**
- Candidate: `98628e98…`, `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- Analysis only. No bot, candidate, detector, gate, harness, host, or Arena change.

## 1. The mechanism, read off the candidate's own source

`resolve_move_conflicts_with_priority_and_forbidden`, readable lines 726–779.

A mover's intended `landing` is `next_cell(walkable, current, target, speed)`. If that cell is
`reserved`, the unit instead takes a **detour**: among orthogonal neighbours of its *current*
cell that are walkable, unreserved and unoccupied, it takes

```rust
.min_by_key(|cell| (toward_goal.get(cell)…, *cell))
```

The exact cycle, with BFS distance to target written as *d*:

1. Unit at **A** (distance *d*). Its next step is the *d−1* neighbour **X**, which a parked peer
   occupies, so **X** is reserved.
2. Every other *d−1* neighbour is blocked or absent, so the minimiser is **B** at distance *d+1*
   (or *d*). The unit moves **A → B**.
3. Next turn, from **B**, `next_cell` recomputes the shortest path to the unchanged target. It
   runs back through **A**, which is now empty — the unit vacated it — so **A** is neither
   reserved nor occupied. The unit moves **B → A**.
4. At **A**, **X** is still blocked. Go to 2.

**The decisive property: the detour is a pure function of `(current, target, reserved,
occupied)`.** It carries no record of where the unit came from, so identical state yields an
identical decision, forever.

Two facts I verified on this candidate rather than assumed:

- **The bot is not stateless — only the resolver is.** `YamoBot` carries per-turn-persistent
  fields including `regeneration_commitments: BTreeMap<i32, PlantKind>`, keyed by unit id. But
  `grep` for `last_pos|prev_cell|history|streak` returns **0**. Adding
  `last_cell: BTreeMap<i32, Cell>` is the same shape as machinery already present. **A memory fix
  needs no new architecture.**
- **Nothing in the loop can change state.** The unit never arrives; the peer is parked (30/34 of
  `claude_1`'s episodes have it standing on a plant, so it is *working*, not stuck); the target
  scorer re-selects the same tree because it is still the best; and by D-1's own definition there
  is no progress event. The loop is closed.

This matches `claude_1`'s D1-A account. I could not falsify it and I do not dispute it.

**Why terminality is opponent-dependent** follows directly: an aggressive opponent fells trees,
which changes the target scorer's answer and dissolves the loop. A passive one changes nothing.
That is the mechanism behind the measured *p* ≈ 0.0097 for zero aggressive opponents in the
terminal mode.

## 2. The finding that I think should reframe this task

I measured whether oscillating games are actually games we lose. They are much worse:

| | n | mean margin | median | wins |
|---|---:|---:|---:|---:|
| terminal oscillation (≥62 turns) | 19 | **+1.58** | +2.00 | 12/19 (63%) |
| no oscillation at all | 208 | **+16.74** | +16.00 | 164/208 (79%) |

A 15-point margin gap. Controlling for map class it barely shrinks — weighted **−13.6** — and it
is sharply concentrated:

| map class | gap |
|---|---:|
| choke_corridor | **−24.7** |
| single_door_tent | −14.8 |
| forest_sparse | −8.5 |
| open_field | **−0.2** |
| orchard_eligible | **+3.5** |

On open maps, oscillation costs nothing at all. On narrow ones the oscillating games are
catastrophically worse.

**And that is exactly why I do not believe fixing it will help.** D176a is a real intervention
study: it drove the long-run rate below yamo's own reference, with zero de-novo oscillation and
all six value gates passing, and the causal effect was **+0.045 margin, CI [−0.024, +0.114]**.

> When an intervention measures +0.045 and correlation measures −13.6, the intervention is
> right and the correlation is confounded.

The most economical reading of both numbers together: **oscillation is a marker of a cramped,
contended position, not the cause of losing it.** The narrowness that makes two units contend
for one tree is the same narrowness that makes the game hard. Removing the pacing does not widen
the corridor. This is the project's own standing lesson — displacement is the default
explanation — applied to itself.

I hold this loosely on one point: my −13.6 controls for map *class*, not for individual map
geometry, and the oscillating games may be the narrowest instances within each class. But that
possibility makes the confound stronger, not weaker.

## 3. Actions

Effect is judged against the acceptance test: **eliminate all 20 terminal episodes**, not reduce
counts.

### A — give the resolver memory

**A1. Forbid immediate backtrack.** Record each unit's previous cell; exclude it from the detour
candidates. ~5 lines, using the existing per-unit map pattern.
*Effect:* breaks every 2-cycle by construction — and all 34 episodes are 2-cycles (`cells` is a
pair in every episode). Plausibly all 20.
*Cost:* hours. *Risk:* genuine dead-ends where backtracking is the only legal move; the unit
would WAIT instead — trading a 2-cycle for a stall that P4 may then flag. Also a 2-cycle can
become a 3-cycle A→B→C→A, which this does not catch.
*Falsified by:* a panel rerun showing any terminal episode remaining, or a rise in P4 stalls.
*Owner needed:* no.

**A2. Forbid the last *k* cells** (k = 3 or 4). Same shape, catches short cycles too.
*Effect:* strictly stronger than A1. *Risk:* more WAITs, more P4 exposure. *Owner:* no.

**A3. Do NOT port the Gold-era watchdog as-is.** `rust/src/botmain/motion.rs` tracks a
*same-position* streak (`troll id -> (x, y, same-pos streak)`, "sidestep after 2 stuck turns").
**An oscillating unit is never in the same position twice running**, so that predicate never
fires on this defect. The task record offered porting it; having read it, I think it is the
wrong tool. Its *distinct camp-cell claiming* is a different matter and belongs under B.
*Owner:* no — but this correction matters, because "port the thing that already works" is the
obvious move and I believe it fails.

### B — remove the precondition, so contention never arises

**B1. The Elost owner rule.** *A capable worker already standing on a live tree owns that tree
for the current decision; do not send a second worker to the occupied cell.* Owner-authored from
exact game `897556967`.
*Effect:* potentially the largest single lever — **34/34 episodes have a parked adjacent peer and
30/34 have it standing on a plant.** It removes the cause rather than the symptom, and unlike A1
it cannot convert an oscillation into a stall, because the second unit gets a *different
productive target*.
*Cost:* larger — it touches target selection, not just movement. *Risk:* `CONSTRAINTS` records
that a broad tent-adjacent coordination layer scored **11.96 at rank 111/113** live; this is a
much narrower rule, but it is the same family and deserves that caution quoted.
*Falsified by:* episodes persisting with no peer on the target, which would refute the 34/34
precondition on this candidate.
*Owner:* yes — it changes bot policy, not just conflict resolution.

**B2. Exclusive target claiming.** Units reserve targets as they already reserve cells.
*Effect:* removes same-tree contention structurally. *Risk:* a claimed-but-unreachable target
starves the claimant; needs release conditions, which is where the banana FSM work repeatedly
failed. *Owner:* yes.

**B3. Price contention into the scorer.** Penalise a target another own unit is closer to.
*Effect:* probabilistic, not structural — will not guarantee zero. *Owner:* no.

### C — change the resolver's architecture

**C1. Joint assignment instead of sequential greedy.** The current loop resolves movers one at a
time in a fixed order; a joint min-cost matching over (unit → landing cell) would never produce a
mutually blocking assignment.
*Effect:* eliminates the class, not the instance. *Cost:* the largest here. *Risk:* a rewrite of
the most behaviour-sensitive function in a bot whose value we cannot currently measure. **I would
not do this while the gate is unready.** *Owner:* yes.

### D — change what we require, rather than what the bot does

**D1. Re-scope the gate condition from "raw D-1 = 0" to "no terminal oscillation".**
*Rationale:* SHORT episodes are **0/15 terminal** — every one self-resolves — and a perfect fix
is worth +0.045. The condition exists so the instrument can certify candidates; a bound on
terminal deadlock achieves that at a fraction of the risk.
*Effect:* makes the gate satisfiable **without touching the bot at all**, which is the cheapest
route to Phase 2 by a wide margin.
*Risk:* it relaxes an owner-standing rule, and the last time an exemption existed the owner
removed it. This must be a *new reviewed gate contract*, never an informal exemption.
*Owner:* **yes — this is the decision I most want made.**

**D2. Question D-1's predicate.** It requires zero progress events *for that unit*. If unit 2
paces while unit 0 works productively, the game may be unharmed — which is precisely what
+0.045 suggests. A per-game predicate ("no progress by any own unit") would measure harm rather
than untidiness.
*Effect:* likely collapses most of the 34 to non-episodes. *Risk:* this is changing the
instrument to pass the test, and needs the same scrutiny as any detector change — dual review,
and the standing rule that an instrument must pass its own reference.
*Owner:* yes.

**D3. Repair the gate's *reference*, not the shipped bot.** The two-sided acceptance test needs
"a repaired reference descendant" that reaches raw zero. **That reference need not be what we
submit.** We could apply A1 to a reference-only build, satisfy the gate, and leave the live bot
untouched until a change earns its place on value.
*Effect:* unblocks Phase 2 with zero risk to the ladder. *Owner:* yes, but it is cheap and
reversible.

### E — bound the damage instead of removing it

**E1. Progress watchdog.** After *N* turns with no progress event, force the unit to take the
best available productive action, ignoring its current target.
*Effect:* converts a 194-turn deadlock into an *N*-turn one. Does not reach zero, so it fails the
stated acceptance test — but it caps the worst case, which is what actually costs turns.
*Owner:* no.

### F — do nothing

**F1.** Extend the existing closure: a perfect fix is worth +0.045, so the correct action is D1
or D3 and no bot change at all. **This is a serious answer, and it is close to my
recommendation.**

## 4. What I would do

**D3 first, then A1 inside it, and D1 put to the owner in parallel.**

Repair a reference-only build with the no-backtrack rule. It is hours of work, structurally
targets the exact 2-cycle every episode exhibits, needs no owner decision, risks nothing on the
ladder, and either satisfies the gate's two-sided test or falsifies A1 cheaply. Meanwhile the
owner rules on D1, because if "no terminal oscillation" is acceptable as the gate condition, most
of this work is unnecessary.

**What I would not do:** C1 while the gate is unready; B1 without the owner, given the 11.96
precedent; and porting the Gold-era watchdog, which I believe cannot fire on this defect.

**What I would most like challenged:** my §2 claim that oscillation is a marker rather than a
cause. If that is wrong, D1 and F1 are wrong with it and the whole priority changes.
