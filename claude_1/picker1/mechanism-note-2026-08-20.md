# Phase 1 mechanism note — WHY the joint pairing benches a working troll

- Task: `20260820-pair-selector-anti-benching` (rule R-2), Phase 1 — WHY, not a fix
- Author: claude_1 · Reviewer: codex_1 (instrument-first) · **Design gate: the OWNER**
- Subject, pinned: `cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs`,
  SHA-256 `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`
- Date: 2026-08-20

## Step 0 — the premise the unblock rests on, measured

`step0-arm-identity-2026-08-20.py` (output: `…-2026-08-20.txt`). The two bots in tonight's
platform session differ by **one hunk, 8 lines**, inside `predicted_opp_chop`. The three regions
that decide the pairing are **byte-identical** in both arms:

| region | sha256 (16) | bytes |
|---|---|---|
| `select()` block (`fn wait` … `fn move_command`) | `8978fca0f9e8375b` | 3626 |
| candidate assembly (`by_id` … the `select` call) | `f7227b5d8cc18f3d` | 2498 |
| `Candidate` / `Target` types | `7e7ec38954f68d49` | 270 |

**How far that reaches, stated precisely rather than inherited.** The deleted hunk feeds
`predict_tree`, which feeds candidate **scores** — so `select()`'s *inputs* can differ between
arms wherever that forecast participates. The **mechanism** below (which clause benches, which
term dominates) is arm-independent. The **per-turn arithmetic** is pinned to the cure-C subject,
which is exactly what the charter pins Phase 1 to. Tonight's verdict cannot move the mechanism.

## The instrument

`make_picker_probe.py` patches four print-only taps into the pinned subject
(`probe-picker1.rs`): a turn tap at the call site, a dump of every candidate the generator
offered each unit with its own score and target, a row for **every pair the selector actually
enumerated**, and the winning pair.

**One scoring path.** The pair rows do not recompute anything. The selector's own
`compatible(a.target,b.target)` and `stock_compatible(a,b,inventory)` calls are hoisted into
`let` bindings and the original `if` reads those bindings, so the logged verdict *is* the verdict
the selector used. That is the standing lesson from the three proxies this programme retracted on
08-15→17.

Two gates run before a single row is read, per situation:

1. **Parity** — `coverage.check_parity`: the diagnostic loop's command stream must be
   byte-identical to `regression_tests.run_binary_custom` on the **uninstrumented** subject. This
   is the licence for the custom loop and for the claim that the probe only prints.
2. **Coverage** — exactly one `PS1TURN` block per window turn, no gaps, no duplicates.

**The guard fired, and that is recorded.** The first classifier asserted that a benched-unit pair
tying the winner was impossible "by construction", and failed the run rather than reporting a
mechanism. It was wrong, and the guard is what found it: the selector's test is `score >
best_score`, **strictly**, so ties are reachable and go to the pair enumerated first. That
retraction produced the second mechanism below.

## Scope actually measured

All **24** `GOAL_SPLIT_WRONG` situations, not only the four the charter required — the four
owner-ruled cases (OSC-004, OSC-013, OSC-017, OSC-034) are inside it and are called out
separately. **2245** benched-with-work turns.

A turn counts as *benched* when the command the selector returned for the situation's unit is
`WAIT` while that unit's **own candidate list** — the generator's output, not an oracle's
opinion — held at least one non-`WAIT` candidate. 360 further turns had no work offered at all
(that is the `NO_GOAL_ASSIGNED` pool, a different task) and are excluded, not counted as benched.

## Finding 1 — the discard is a HARD FILTER, and it is `compatible()`, on 2245 of 2245 turns

| blocker at the winner | turns |
|---|---|
| `INCOMPATIBLE_TARGET` (`compatible()` — same target cell) | **2245** |
| `STOCK` (`stock_compatible()`) | 0 |

`compatible()` returns false when both targets resolve to the same cell. On **every** benched
turn, the benched unit's best real candidate was excluded against the partner's *winning*
candidate by that clause. `stock_compatible` never bit once.

This is not incidental — it is forced. With the partner's choice held fixed, a positive-scored
candidate of mine that survived both predicates would out-sum `WAIT` (score `0.0`) and the
selector could not have benched me. **So whenever a troll holding real work is benched, the
target-collision filter is necessarily implicated.** The probe confirms the prediction on all
2245 turns rather than leaving it as an argument.

## Finding 2 — with the pair excluded, the arithmetic splits two ways

| resolution | turns | who dominates |
|---|---|---|
| `SCORE_PREFERENCE` — the partner's term is larger, so the pair (`WAIT`, partner works) wins | **1435** | PARTNER, 1435/1435 |
| `TIE_ENUMERATION_ORDER` — the two one-works pairs tie exactly | **810** | decided by iteration order |

Ties: `score > best_score` is strict, the outer loop runs `ids[0]`'s list, and `WAIT` sits at
index 0 of it. So on a tie the pair found first — *`ids[0]` waits, `ids[1]` works* — keeps the
crown. Prediction: the benched unit in every tie case is the **lower-id** unit. Observed:
**10 of 10** tie situations bench unit 0. The bench is decided by loop order, not by value.

The winning pair's value was positive on all but one situation (OSC-031, 167 turns at sum ≤ 0 —
its own separate story, and it is the `NO_GOAL_ASSIGNED` case anyway).

### The four owner-ruled cases, exact arithmetic

| case | turns | class | benched unit's work | partner's kept command | scores | margin |
|---|---|---|---|---|---|---|
| OSC-017 | 194 | SCORE_PREFERENCE | `CHOP 0` | `MOVE 2 10 0` | 222.22 vs 375.00 | 152.78 |
| OSC-013 | 187 | SCORE_PREFERENCE | `CHOP 0` | `MOVE 2 8 2` | 86.96 vs 150.00 | 63.04 |
| OSC-034 | 94 | TIE | `CHOP 0` | `MOVE 2 2 3` | 500.00 vs 500.00 | 0.00 |
| OSC-004 | 12 | 3 TIE + 9 PREF | `CHOP 0` | `MOVE 2 10 1` | 86.96→285.71 vs 86.96→333.33 | 0.00–63.49 |

In OSC-013 and OSC-017 the identical row repeats **187 and 194 times** — same commands, same
scores, same margin. Nothing in the state moves, so the decision cannot change.

## Finding 3 — the preferred alternative is one the picker itself makes impossible

The referee drops a `MOVE` into an occupied cell unless the occupant vacates
(`sim/engine.py:134-150`). `deadlock_check.py` asks whether the partner's *winning* command is a
`MOVE` onto the cell the benched troll is standing on:

| | turns |
|---|---|
| partner's kept command is a MOVE **onto the benched troll's own cell** | **2010** (89.5%) |
| partner moves elsewhere (target collision not on the unit's cell) | 235 |
| **all four owner-ruled cases** | **100% onto the benched troll's cell** |

So the dominant shape is a self-inflicted deadlock. The benched troll is **standing on the tree**
and offers `CHOP`. The partner is offered a `MOVE` onto that same square, scored higher because
it is a forecast of chopping that tree later. The selector prefers the promise, and in the same
breath orders the only unit that could vacate the square to `WAIT` — so the promise cannot be
kept this turn, and nothing changes, so it cannot be kept on any turn. Measured: the benched unit
occupies one cell for the whole window in the four cases; the partner oscillates between at most
two (`partner-arrival-2026-08-20.json`). Up to **194 consecutive turns** of both trolls idle.

**The picker prefers work-in-hand's promise over work-in-hand, and its own choice is what
falsifies the promise.**

## What this note does NOT claim

- It does not say `compatible()` is wrong to exclude same-cell pairs. It says the **resolution**
  of that exclusion benches a unit, and names the arithmetic.
- The 235 non-deadlock turns (OSC-002 189, OSC-001 26, OSC-029 14, OSC-031 6) are a genuine
  second shape — contested target, partner headed elsewhere — and are **not** explained by
  Finding 3. Any fix must state what it does about them.
- Nothing here is measured on the Door-1 arm. Step 0 shows why it need not be for the mechanism,
  and says where the numbers could differ.
- No fix is built, and none may be until the owner rules on the design below.

## Fix design PROPOSAL — for the owner's design gate

The picker is planner core; the two-doors wall applies; these are proposals, not decisions.

**P1 — refuse the pair the picker itself makes impossible** (recommended).
Inside the same pair loop, drop a pair in which one unit's command is a `MOVE` onto a cell whose
occupant is our own unit that the same pair orders to `WAIT`. Reads only what the pair already
holds. Narrow, mechanically checkable, and addresses **2010 of 2245** turns and **4 of 4**
owner-ruled cases directly. Risk: the smallest blast radius of the four; it removes only choices
the referee was going to discard anyway.

**P2 — break ties toward fewer `WAIT`s** (recommended alongside P1, independently cheap).
Change the tie-break so an equal-sum pair that employs both trolls, or employs the currently
idle one, beats the one found first. Closes the 810 tie turns on its own merits and removes a
behaviour decided by `BTreeMap` key order — which is not a decision anyone designed. Risk:
touches every tie in every game, not only these; needs the full named-costs decomposition.

**P3 — price the bench** (larger, not recommended for the first cut).
Score `WAIT` as the negative of the unit's own best forgone candidate, so benching costs what it
gives up. Principled and would subsume P1 and P2, but it changes the value of **every** selection
in every turn of every game. Blast radius is the whole planner.

**P4 — discount promises against work in hand.**
Deflate a forecast-scored `MOVE` relative to an executable `CHOP`/`HARVEST` this turn. Attacks
the root asymmetry (222.22 in hand losing to 375.00 in prospect), but requires a defensible
discount factor, which is a new tuning surface and a new way to be wrong.

**My recommendation: P1 + P2**, as one candidate, with the 235 non-deadlock turns explicitly out
of scope and named as such rather than quietly hoped away. If the owner wants the root asymmetry
addressed rather than the deadlock, that is P4 and it is a different, larger piece of work.

Phase 2, whichever way the owner rules, is the named-costs gate class with its own platform
session, fail-first fixtures on the four ruled cases, on **whatever resident tonight settles**.

## Artifacts

| path | what |
|---|---|
| `claude_1/picker1/make_picker_probe.py` | probe builder (digest- and anchor-guarded) |
| `claude_1/picker1/probe-picker1.rs` | the probe, `6b5a718d…` — diagnostics only, never a candidate |
| `claude_1/picker1/probe.py` | runner: parity gate, coverage gate, classifier |
| `claude_1/picker1/mechanism-2026-08-20.json` | the four owner-ruled cases |
| `claude_1/picker1/mechanism-all24-2026-08-20.json` | all 24 `GOAL_SPLIT_WRONG` situations |
| `claude_1/picker1/deadlock_check.py` + `deadlock-all24-2026-08-20.json` | Finding 3 |
| `claude_1/picker1/partner-arrival-2026-08-20.json` | the four cases' unit positions across the window |
| `claude_1/picker1/step0-arm-identity-2026-08-20.py` + `.txt` | step 0 |
