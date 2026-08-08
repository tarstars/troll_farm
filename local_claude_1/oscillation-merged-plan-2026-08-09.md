# Oscillation: the merged plan from three independent answers

- Task `20260809-oscillation-attack`; merged by `local_claude_1` as integrator
- Sources: `chatgpt_1` (`20260809T112000Z`), `claude_1` (`20260809T143000Z`), and my own
  (`1c65c9fc` + amendment `5d775ddb`)
- All three state they published without reading the others. **Disagreements are preserved
  below, not averaged.**

## The headline

**The obvious fix does not work, and we now know that before building it.** That is the whole
return on running this three ways.

`claude_1` measured it: every D-1 step is **ADVANCE or RETREAT, zero LATERAL**, so a
monotone-or-hold mover invariant removes **34 of 35 episodes** — but **20 of 20 terminal
blockers never move at all**. A mover-only fix therefore **converts 20 oscillations into 20
stalls and restores progress in none of them.** The detector goes quiet; the program is exactly
as stuck.

That refutes my own primary recommendation (no-backtrack in the shipped bot), and it is precisely
the outcome the owner's objective forbids: a number made acceptable without control gained.

## Where all three independently agreed

1. **The memoryless detour is the proximate mechanism.** A blocked step becomes a one-turn
   detour computed as a pure function of current state; next turn the direct step returns.
2. **The Gold-era watchdog cannot be ported as the fix.** `chatgpt_1` and I found this
   separately: it counts a *same-position* streak, and an oscillating unit changes position every
   turn. Two independent negative results on the task record's own suggestion.
3. **A mover-only change is insufficient.** Reached three different ways — my stall risk,
   `chatgpt_1`'s interface argument, `claude_1`'s 20/20 measurement.

## What each answer contributed uniquely

### `claude_1` — three findings, two of which change what we build

- **The `Target::None` bypass.** `compatible` returns `true` unconditionally when either target
  is `Target::None` (candidate line 643; sacred source 1329). **This answers the standing
  question I posed and refutes my own correction**: same-target contention *does* survive the
  pairwise check. I had pasted this exact code and read only the `a != b` branch.
- **D1-B localised for the first time**, at `endgame_candidates:1290-1302`: a unit standing on a
  door prices only that door, valuing the same plan ~25% higher one step off it. This was
  `UNRESOLVED` in `claude_1`'s own earlier scoping. It matters disproportionately because **raw
  zero is conjunctive** — that single unlocalised episode was enough to block everything.
- **The 20/20 never-move measurement** above.

### `chatgpt_1` — the defect is an interface, not a function

The planner already rejects equal target cells but **does not model route or first-landing
compatibility with a stationary working peer**; the resolver then rewrites the blocked MOVE into
a detour, and **that override is never fed back into target validity, commitment or scoring**. So
two locally correct stateless functions compose into a terminal deterministic involution. Its
naming of the salvageable Gold components is the constructive part: joint landing solver,
stationary-worker obstacles, a **stay option**, non-negative progress, canonical whole-vector
tie-breaking.

### Mine — what survives

The verified mechanism and that **all 34 episodes are 2-cycles between orthogonally adjacent
cells**; that the bot carries per-unit state but has zero position memory; that yamo shipped this
knowingly (*"I only set the destination, which meant my trolls occasionally blocked each
other"*); and the margin analysis — oscillating games average **+1.58 against +16.74**, −13.6
after map-class control, while D176a's *causal* value is +0.045. Those 19 games hold an
undiagnosed problem and are a free diagnostic set.

## The merged plan

**Principle, from combining `claude_1`'s 20/20 with `chatgpt_1`'s interface argument: because the
blocker is stationary and productively working, the moving unit must _re-target_, not _re-route_.**
No amount of cleverness in the mover helps when the obstacle will never leave.

1. **Fix the `Target::None` bypass** (`claude_1`). Smallest, most local, and it restores the
   coordination the design already intended. Needs care: `None` presumably exists so a WAIT
   pairs with anything.
2. **Fix D1-B's door-pricing asymmetry** at `endgame_candidates:1290-1302` (`claude_1`).
   Independent of everything else and mandatory, because raw zero is conjunctive.
3. **Add route/landing compatibility to the pairwise target enumeration** (`chatgpt_1`) — the
   planner must treat a stationary working peer as an obstacle when it scores a target, so the
   contended target is never selected. This is the load-bearing change.
4. **Give the mover a stay option** (`chatgpt_1`) so that when it is blocked it holds instead of
   retreating. On its own this is the stall-generator `claude_1` warns about; behind (3) it is
   the correct terminal behaviour.
5. **Freeze the 20 terminal rows as regression fixtures** (`chatgpt_1`), plus a test that
   reproduces a 2-cycle and fails without the fix. **Under the owner's objective the test is the
   deliverable, not the number.**

**Acceptance, unchanged and now sharper:** all 20 terminal episodes gone **and** progress restored
in those games — not merely the detector silent. `claude_1`'s finding makes "D-1 = 0" alone an
insufficient acceptance criterion, since a stall satisfies it.

## Preserved disagreement

`claude_1` presents the corridor block as the primary mechanism; `chatgpt_1` presents the
planner/resolver interface as primary and the detour as a symptom. **These are the same defect
described at different altitudes** and the merged plan acts on both, but they are not identical
claims and I have not forced them into one.

Unresolved: whether fixing (1)–(4) restores progress in the 19 low-margin games or merely removes
the pacing. My margin analysis says something else is wrong in them. Nobody has diagnosed it.

## Corrections to my own answer, on the record

- My correction message told both peers that "same-tree contention" was probably the wrong label.
  **Wrong** — `Target::None` is the mechanism by which it survives, and it was in code I quoted.
- My recommended fix (no-backtrack in the shipped bot) is **withdrawn as a primary action**; it
  is step 4, and only behind step 3.
