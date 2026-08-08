# Manifest: make the bot's intentions legible

- Author: owner, 2026-08-09. Transcribed and annotated by `local_claude_1`.
- Status: **FOR REVIEW by all agents.** Nothing here is scheduled work yet.
- Subject bot: `readable__no_orchard` (`98628e98…`) and the shared lineage behind it.

## The owner's statement

1. Our current bot's logic is defined by **assigning weights to actions**.
2. That weight assignment is **not transparent**: it effectively hides the algorithms the
   trolls are following. In conversation the owner has stated what the trolls' logic is and
   agents have disagreed — *because of this opacity*, not because anyone was careless.
3. Our task is to build a **bridge between the trolls' algorithms and the weighting approach**.
4. Our task is to build **tooling to analyse, test and debug** this system's behaviour.
5. For oscillation specifically: build a **library of the situations in which oscillations
   occurred**; **independently work out the best course of action** in each; and **compare that
   with what the combined-score approach actually chose**.
6. Review the scoring approach carefully. It appears that **intention is encoded as "big steps"**
   in the score. Check that the **hierarchy is correct**, and that **sums of sub-scores do not
   cross the boundaries between intentions**.

## Why point 2 is not a complaint about anyone

This has cost us real time and it is worth stating plainly. Within the last two days:

- The coordinator told both agents that "same-tree contention" was the wrong explanation for the
  oscillation, having read `compatible()` and seen its `a != b` branch. It missed that the same
  function returns `true` unconditionally when either target is `Target::None`. `claude_1` found
  it. **Two competent readers of the same twelve lines reached opposite conclusions.**
- The coordinator also suggested reusing a retired anti-stall watchdog; two agents independently
  showed it could never fire.

Neither error was carelessness. Both came from the same source: **you cannot read an intention
off a number.** The score says *3900*; it does not say *"this troll is trying to deny the
opponent a lemon."*

## What the code actually looks like (verified, for review)

There is a real band structure. Values found in the candidate:

| band | value | what it attaches to |
|---:|---|---|
| forced | `20_000.0` | unblocking moves; `DROP` by a blocking unit |
| override | `10_000.0` | an endgame path that overwrites a computed score outright |
| pick | `7_500.0 - priority` | `PICK` a fruit |
| return | `7_000.0` | `MOVE` to our own shack |
| work | `base_score + 900.0` | `HARVEST`, `MINE` |
| work | `1000.0 * wood / turns` `+ 900.0 / (1 + opponent_distance)` | `CHOP`, plus the denial bonus |

Two properties in that table are exactly what point 6 asks about, and both are checkable:

**(a) Additive terms can cross a band.** A chop is `1000 * wood / turns`, and `wood` is capped by
carry capacity (≤3) while `turns` is floored at 1 — so the base alone reaches **3000**, and with
the denial bonus **3900**. Whether that can overtake a `HARVEST` depends entirely on the
`base_score` its caller passed. **Nothing in the code prevents a well-priced chop from
outranking a differently-intended action.** Whether it *should* is a design question nobody has
recorded an answer to.

**(b) The band is set by the caller, not the action.** `fruit_candidates(..., base_score)` and
`iron_candidates(..., base_score)` take the band as a **parameter** and add `+900.0` inside. The
same function therefore emits scores into different bands depending on who called it. That is
the opacity of point 2 in miniature: **the intention lives at the call site, the number lives in
the function, and neither is written down.**

## What is being asked for — for review, not yet scheduled

**A. The bridge (point 3).** Some artifact that maps *intention* to *number*: for each scoring
site, what the troll is trying to do, which band that intention belongs to, and why. A table, a
typed wrapper, named constants, a specification — the form is open. The test of success is that
the owner can state a troll's logic and an agent can confirm or refute it **by pointing at the
bridge**, not by re-deriving it from arithmetic.

**B. Tooling (point 4).** Analyse, test, debug. At minimum: given a game state, show every
candidate action with its score, its band, and its intention; and given a decision, explain why
*this* action beat the alternatives.

**C. The oscillation situation library (point 5).** We already have the raw material: **34
episodes across 32 games**, with map, seat, unit, turn range and the two cells. The work is to
freeze them as inspectable situations, decide **independently** what the right move is in each,
and compare against what the scorer chose. Note this is a stronger test than any we currently
run — it asks whether the decision was *correct*, where today we only ask whether it *oscillated*.

**D. The hierarchy audit (point 6).** Enumerate the bands; verify the ordering is the intended
one; and prove — or find counterexamples to — the claim that a sum of sub-scores cannot cross
into a band above it. Item (a) above suggests counterexamples exist.

## Why this may matter more than the oscillation itself

The oscillation exercise produced its result because `claude_1` measured what the *blocking*
troll was doing — a question the brief never asked. That was luck arising from independence. **A
bridge and a debugger would turn that kind of finding from luck into routine.**

It also bears directly on the standing problem that our acceptance gate cannot certify anything:
several of this week's failures were instruments that measured something other than what they
claimed. A scoring system whose intentions are unwritten is the same class of defect, one level
down.

## For reviewers

Attack, specifically:

- **Is the "big steps encode intention" reading correct?** It is the owner's, and the band table
  supports it — but the bands may be historical accident rather than design, in which case the
  audit's premise changes.
- **Is a bridge maintainable?** A mapping that drifts from the code is worse than none, and this
  project has already been burned by documents that outran their implementation (D-6 enforces a
  predicate its own design document retired).
- **Is item C worth it before the measurement apparatus is repaired?** The panel is currently
  `GATE_UNREADY`.
- **Scope.** This is four substantial deliverables. Which single one, done first, would have
  prevented the most of this week's wasted effort?

Reply with a review, not an implementation. No code, no candidate, no gate or detector change is
authorised by this manifest.
