# Frozen DESIGN/PLAN — policy-anchored macro rollout controller (run 062139Z)

Frozen BEFORE any source edit. New family `claude_candidate_macroplan*`; the
dispatch family is untouched and read-only.

## Macro family (one, economically justified)

**Funded third worker.** The unchanged parent (`95ee691e`, `can_train`) caps its
own roster at 2 and never funds a third troll. A third troll is a *complete*
economic plan, not a scalar job rate: it costs banked fruit now
(`training_cost(n=2, talents) = 2 + t^2` in PLUM/LEMON/APPLE/IRON, i.e. real
score removed from the bank this turn), it competes with the two existing
workers for the same finite trees and the same door traffic, and it repays only
over many later turns of travel/harvest/chop/bank. That is exactly the
"finite resources, growth delay, workforce funding, competing own workers"
hypothesis, and it cannot be decided by a per-job rate.

## Roots (parent always available), horizons, opponents, selection

* Root 0 = the parent's own authoritative joint commands for this turn
  (`SearchBot::commands`), unchanged.
* Root 1/2 = the same parent joint commands **plus** one predeclared
  `TRAIN` — SPEC_A `(2,2,1,1)` porter, SPEC_B `(2,1,0,2)` chopper — offered only
  when the referee's own affordability rule passes on all six stocks. Unit
  commands, seeds, cargo and plot ownership stay exactly the parent's; the bill
  is shared funding out of the same bank.
* Each root is executed through the **actual referee** (`parity::step_direct`)
  for `MACRO_HORIZON = 24` turns, checkpoints at 12 and 24, identical for every
  root. Root turn: real commands both sides. Continuation: a cheap deterministic
  economic model policy (nearest reachable fruit, else chop, carry home, DROP,
  one target per worker) on **both** seats — this is a MODEL, not a prediction
  of either real policy.
* Opponent: the root-turn hypothesis is the parent's adaptive V439 opponent
  policy (identical for all roots); two predeclared cheap continuations —
  H0 "own-side" and H1 "contests our door" — and the value of a root is the
  **min** over both hypotheses and over both checkpoints (conservative).
* Accept the best alternative only if that conservative gain
  `>= MACRO_MIN_GAIN = 1.0`; otherwise issue the parent commands unchanged.
* Any `Unsupported`/critical-issue rollout ⇒ deterministic parent fallback.

## Budget (deployment-relevant)

Window `40 <= turn <= 200` (strictly below the parent's `START_TURN = 220`, so a
macro turn never coincides with the parent's own search), `>= 60` turns left,
roster exactly 2, no parent TRAIN in the turn, `>= 8` turns between evaluations,
at most 6 evaluations per game. Worst case 3 roots x 2 hypotheses x 24 referee
steps on a turn where the parent does no search.

## Memory and cancellation

Nothing speculative is stored: the parent's memory is committed by its own call,
the controller stores only the spec it actually issued and re-decides from the
real state every turn. Alternative evaluation runs on clones
(`parity::from_game(g.clone())`, cloned policies) and never touches parent
memory. Roster change, endgame (`>=60` turns left), unreachable targets, budget
exhaustion and opponent action all close the window or fall back to the parent.

## Comparison and decision rule (frozen)

Baseline: policy-flat parent `95ee691e`. 192 pairs 9947500..07, 12 adaptive
opponents, both seats, `ALLOW_ANY_MAP_SEED=1`; all 192 baseline command arrays
must match gap `20260906T210944Z-3184968-1`. Positive whole-panel W+0.5D AND 0
candidate issues supports further evaluation. No post-panel tuning, no scan.

## Predeclared variant B — frozen 2026-09-07 06:36Z, BEFORE any panel result

The focused fixture run (`tests-2.log`) shows the controller evaluating and
rejecting cleanly (evaluations 6, activations 0, aborts 0) and the rollouts are
far cheaper than budgeted. A 24-turn horizon structurally cannot contain the
payoff of a bill of 11-15 banked points, which contradicts this plan's own
requirement that the budget include the real payoff. Variant B is therefore
predeclared now, before `panel.tsv` exists and without reading any panel row:

* Variant A = `MACRO_HORIZON 24`, `MACRO_MID 12` (panel already running).
* Variant B = `MACRO_HORIZON 60`, `MACRO_MID 30`; every other constant, spec,
  opponent hypothesis, window and selection rule identical.

Both variants are run on the same frozen 192-pair panel and both results are
reported, whatever they are. No third variant, no other constant changes, and
no selection of a "best" variant from this development panel.
