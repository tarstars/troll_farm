# 20260809-oscillation-attack: why `readable__no_orchard` oscillates, and every way we might stop it

- Status: open — assigned to all three agents in parallel, owner-directed 2026-08-08
- Record owner: local_claude_1
- Work owners: **local_claude_1, claude_1, local_codex_1 — independently, in parallel**
  (`local_codex_1` reassigned 2026-08-12 from `chatgpt_1`, out of reach. Three independent
  answers is the design; if `local_codex_1` cannot start, the task proceeds on two and that
  reduction must be stated in the merged plan, not silently absorbed.)
- Reviewer: cross-review after all three answers are published
- Integrator: local_claude_1
- Area: D-1 oscillation on the `readable__no_orchard` lineage
- Base commit: cfc4e4eb2206
- Created UTC: 2026-08-09T07:00:00Z

## Outcome

Three independent answers to one question, then one merged plan: **why does this candidate
oscillate, and what could we do about it?**

## The candidate — exactly this bot, nothing else

| field | value |
|---|---|
| reference name | **`readable__no_orchard`** |
| source | `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` |
| SHA-256 | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| why this one | only human-readable submitted source; smallest real code we have (46,859 chars); highest mature score measured (24.76, rank 21/137) |
| full record | `docs/reference/readable__no_orchard.md` |

It is readable, which is the point: **you can read the defect rather than infer it.**

## What we want to fix

D-1 oscillation: a unit alternating between two adjacent cells with **zero progress events** —
no carry change, no inventory change, no plant created or removed.

Measured on this exact candidate, 240-game panel
(`local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json`):

- **34 episodes across 32 of 240 games**;
- median 155 turns; **worst 194 turns of a 200-turn game**;
- **20 of 34 are the terminal mode** (≥62 turns), which mostly never resolves;
- the second worker accounts for 25 of 34.

**The same 32 of 32 `(map, seat)` pairs oscillate in the banana parent `a8eb3b2b`.** The defect
is inherited from the shared movement core and has nothing to do with the orchard, which this
candidate does not have.

## ★ Read this before proposing anything: the standing closure

`docs/CONSTRAINTS.md` says, and it is not being overturned:

> **Oscillation is CLOSED permanently after two designed attempts.** D176a's preference
> tie-break with bounded arming largely worked — ≥10-turn task rate 8.50% → **2.88%**, *below
> yamo's 2.9% reference*, with **zero** de-novo oscillation and **all six value gates passing**
> — and it is still worth only **+0.045 overall margin (CI [−0.024,+0.114], ≈0.005 rating)**. A
> working version of this fix does not justify a promotion cycle. Do not reopen. [D176a; D171a]

**That closure stands, and it is about VALUE.** Nobody should propose oscillation work on the
grounds that it will raise our score; that hypothesis is measured and dead. A *perfect* fix is
worth about +0.045 margin.

**The justification is the owner's, restated 2026-08-09, and it is not score and not merely
gate compliance:**

> *Oscillations are our lack of control over the program. I want to remove them not in order to
> immediately improve score, but to reduce technical debt, improve our test coverage and
> understanding of the situation.*

**Success is therefore:** the shipped bot cannot enter a 194-turn no-op; a committed regression
test fails if it ever can again; and we can explain why the design permitted it. Instrument
compliance (raw D-1 = 0 unblocks the gate, and Phase 2 turns on it) is a welcome by-product, not
the objective.

This ranking follows and is binding: **an action that satisfies a threshold without increasing
what we control is a worse answer than one that increases control.** Relaxing the gate condition
and repairing only a reference build both fall in the first category; I proposed both and have
withdrawn them.

Any answer that claims score improvement will be rejected on the citation above. An answer that
says "the cheapest route is to change what we require rather than what the bot does" is
**explicitly welcome** — see below.

## What is already established — do not re-derive, do attack

1. **Mechanism, from the candidate's own source**
   (`resolve_move_conflicts_with_priority_and_forbidden`, readable lines 726–779). A unit whose
   next step toward its target is `reserved` takes a **detour**: the orthogonal neighbour of its
   *current* cell minimising `(distance_to_target, cell)`. That choice is a pure function of
   `(current cell, target, reserved, occupied)` — **it has no memory of where the unit came
   from**. Next turn it recomputes from the new cell, and the minimiser is frequently the cell it
   just left.
2. **Root cause split** (`claude_1`,
   `claude_1/banana-restoration-r2/feasibility-raw-zero-2026-08-07.md`): **D1-A = 34/35**,
   same-tree contention against that memoryless tie-break, with resolver replay reproducing every
   non-terminating turn; **34/34 have a parked adjacent peer, 30/34 with that peer standing on a
   plant**. **D1-B = 1/35**, a goal-selector two-cycle.
3. **Why it never terminates.** Nothing in the loop changes state: the unit never arrives, the
   blocker is parked, the target scorer keeps re-selecting the same tree, and by definition there
   is no progress event.
4. **Why the terminal mode is opponent-dependent** (`local_claude_1/d1-mode-structure-2026-08-08.md`):
   counting distinct games, the ≥62-turn mode has **zero aggressive opponents** against a 30%
   panel share, p≈0.0097. Hypothesis, untested: an aggressive opponent keeps changing the board,
   which dissolves the parked-peer precondition before the bounce becomes permanent.
5. **A prior architecture already solved this class.** `rust/src/botmain/motion.rs` from the
   retired Gold-era lineage carries an **anti-stall watchdog with per-troll position memory**
   (`troll id -> (x, y, same-pos streak)`, "sidestep after 2 stuck turns") and **distinct
   camp-cell claiming** so units "don't converge on one cell and block each other", described
   there as *the #1 near-camp block fix*. The current resident has neither. That bot was retired
   for unrelated reasons at a much lower score; the *mechanism* may be portable without the rest.

## What each agent must produce

An artifact on your canonical branch answering three things:

1. **Why.** Your own account of the cause, verified against the candidate's source or by
   execution — not a restatement of §4 above. Say explicitly if you think the established
   account is wrong.
2. **A wide list of possible actions.** The owner's instruction is that this list should **not**
   be limited to "test the code, fix the code". Directions that count, non-exhaustively:
   - change the mover — detour memory, hysteresis, commitment, symmetry-breaking salt;
   - change target selection so contention never arises — e.g. the **Elost owner rule** (a
     capable worker already standing on a live tree owns it; do not send a second worker to the
     occupied cell), exclusive target claiming, or pricing contention into the scorer;
   - change the resolver's architecture — joint assignment rather than sequential greedy, swap
     and chain support;
   - **port** the Gold-era watchdog and distinct-claiming instead of inventing a fix;
   - **change what we require**: is raw D-1 = 0 the right gate condition, or should it be "no
     terminal oscillation", given that SHORT episodes always resolve and a perfect fix is worth
     +0.045? This is a legitimate answer and needs the owner, not us;
   - **change the detector**: is D-1's zero-progress-event predicate measuring harm, or measuring
     a unit pacing harmlessly while its partner works?
   - change the harness, the panel, the opponent mix, or the map generator;
   - do nothing, with an argument.
3. **For each action**: expected effect on the 20 terminal episodes, cost, risk, what would
   falsify it, and whether it needs the owner.

### The acceptance test any proposed fix must meet

From `d1-mode-structure-2026-08-08.md`: **a correct fix must eliminate the terminal mode
entirely — all 20 episodes — not merely reduce counts.** D176a passed its own gate perfectly and
left the worst run unchanged at 247 turns. "The numbers improved" is not evidence.

## Boundaries

**Analysis and proposal only.** No bot edit, no candidate, no detector or gate edit, no host
value protocol, no TestSession, no submission, no Arena action. The resident stays byte-exact at
`fff6669b` and this candidate at `98628e98`.

Note the panel is under `GATE_UNREADY` (referee discards `TRAIN`). It does not void D-1 work: the
ruling names D-9 and P4, the defect touches only map `m040`, and `m040` contributes **zero** D-1
episodes. Say so if you disagree.

## Why three independent answers before any discussion

Each of us has been wrong this week in a way review caught, and convergence reached separately is
worth more than agreement reached in conversation. **Do not read another agent's answer before
publishing your own.** State in your artifact that you did not.

## Handoff

Publish to your canonical branch and hand off by exact path. I merge the three into one plan and
return it to the owner with the disagreements preserved, not averaged away.
