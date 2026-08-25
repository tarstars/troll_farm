# Candidate 2 (the swap) — stop and ask: the pair can trade places every two turns, and one map loses 75 points (owner question, 2026-08-25)

Task `20260825-dance-cure-candidate-2-swap`, under your ruling of this afternoon (swap, no lock,
the swap back impossible by construction and proved — rule R-1a). Plain words; every code
explained at first use. **Nothing has touched the ladder; nothing will until you rule.**

## Where it stands

The design gate passed in 21 minutes: the exact rule and the proof were accepted by `codex_1`.
The build is done and correct: three arms from one source, and with the rule switched off the
bot is **byte-for-byte the champion** on all 34 frozen situations and all 240 panel games. With
the rule on, on the same 240 games:

| | rule off (= champion) | rule on |
|---|---|---|
| dances (a troll bouncing ≥ 7 turns with no progress) | **27 on 25 games** | **13 on 12 games** |
| trolls blocking each other | 0 | 0 |
| every other detector | unchanged | unchanged |
| exchanges fired | — | 46 on 28 games |

The proof held on the wire: over 48,000 panel turns **no pair ever swapped back on the next turn**
(the control that would have falsified it stayed at zero).

## The two findings — both from controls we committed to before counting

**1. The pair can trade places every *second* turn (on 4 of 240 games, and 2 of 34 situations).**
The proof says a swap back needs the planner to move the displaced worker's goal past its old
square — and that is exactly what happens: the swap pushes the worker one square back, the
planner re-picks its goal (the nearest tree is now a different one, beyond the square it just
left), and the rule fires the other way two turns later. Cleanest case, two trolls after two
adjacent trees: turn 3 swap, turn 4 one chops while the other waits, turn 5 swap back, turn 6 the
other chops … to turn 11. Neither troll is parked — each gets one chop per cycle — but the pair
alternates instead of one of them going elsewhere. Every single exchange is legal under the rule;
the loop is the planner's re-targeting, which the exchange itself provokes. The rule's own tick
budget (≤ 1 exchange per 50 turns) is breached on the same games.

**2. One map, `m061`, loses 75 points across its two seats** — 39 on a seat where the champion
had **no dance at all** and the rule fired once; 36 on the other with two exchanges. Over the 240
games the score is net **−24**: seven games improved by +51, that one map −75. (On the 34 frozen
situations the sign is the other way: 5 better, 1 worse, net +35.) This is not diagnosed yet and
no counter predicted it; it is the number that would decide the score block if it generalises.

## What is happening now without you

`m061` is being read turn by turn from the wire (both trolls' goals before and after the exchange,
what each did for the next 20 turns) — the mechanism will be on the record in plain words. The
loop games are being laid out the same way (who re-picked, to what, and what a troll that *kept
its goal* would have done). The remaining controls that do not depend on your answer — the poison
arm, the positive control, the referee check that the exchange really executes, determinism, the
orchard-map check, the per-troll safety net — are being run so the evidence is complete whichever
way you rule.

## Your decision — the loop

Per your rule, nobody adds a lock, a timer or a cooldown. The options:

- **A. A planner rule first (Candidate 3): "a troll keeps its goal."** Once chosen, a goal is kept
  until it is done or gone, or something clearly better appears (a margin). Then the displaced
  worker keeps wanting its old square, which the rule forbids swapping for (the mover's goal must
  lie *beyond* the partner's square), so it simply steps back when the other moves on. One simple
  rule, in the planner where the defect is. Costs one more build + panel before any read.
- **B. Back to the design gate for the swap rule itself** — e.g. only displace a worker whose goal
  is its own square. That is a predicate change, needs a new proof, and may re-introduce cases
  that are not curable without a swap.
- **C. Proceed to the real-game read with the loop measured**, on the argument that it is 4 games
  in 240 while the rule halves the dances. Not before `m061` is understood — a read costs the
  ladder slot and the loop would show up in real games too.
- **D. Stop Candidate 2.**

**My recommendation:** A, after the `m061` diagnosis lands (hours, not days) — the loop is the
planner flipping goals, which is the defect the design predicted and your rule assigns to the
planner; "keep your goal" is the kind of simple rule you asked for. If `m061` turns out to be the
exchange doing damage on its own, that changes the picture and I will say so.

## Where everything lives

`claude_1/cure2/g1-interim-2026-08-25.md` (the report), `claude_1/cure2/definitions-g0-2026-08-25.md`
(the rule and the proof, Addenda A/B), `codex_1/reviews/dance-cure-candidate-2-swap-g0-2026-08-25.md`
(the acceptance), `claude_1/cure2/results/` (every panel game, the loop evidence with actual cells
and targets), all at `agent/claude_1@714935df`; my disposition
`coordination/messages/local_claude_1/20260825T173045Z-…-policy.md`; the task record
`coordination/tasks/20260825-dance-cure-candidate-2-swap.md`.
