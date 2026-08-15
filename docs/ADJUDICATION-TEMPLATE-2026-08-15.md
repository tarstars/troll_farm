# Situation adjudication template — OWNER-RULED 2026-08-15

- **Owner ruling, 2026-08-15 (conversation with `local_claude_1`):** this template REPLACES the
  "goal-hierarchy doctrine" approach for deliverable D3 of
  `coordination/tasks/20260815-oscillation-deep-dive.md`. The rejected draft worked bottom-up
  from the code's score bands; judging the bot against a cleaned-up copy of itself moves
  nothing forward. Judgment is TOP-DOWN, from the game, per situation.
- **Why the priorities are not frozen in advance (owner, verbatim in effect):** *a clear set of
  rules which allow the bot to win this game is the heavy-lifting point of this project, and
  figuring it out is real work.* The rules are the OUTPUT of the 34 adjudications, not an input
  to them. They accumulate in `docs/RULES-LEDGER.md`, owner-approved entries only.
- Consistency across rulings comes from the owner being the judge in every session, and from
  every ruling exposing its reasoning at all four levels below.

## The template — every ruling walks four levels, top to bottom

Each level must be explicitly written and justified before descending. No level may cite
scores, bands, or code — the game only. The code enters at step 5.

**L1 — Read the game state.** Phase (opening / middle / endgame), what resources remain on the
map, score and roster standing (ours and theirs), anything special about this map.

**L2 — Name the current best course of action.** One sentence, chosen FOR THIS SITUATION and
justified from L1. Example: "deny the opponent's camp."

**L3 — State the best joint behavior.** What BOTH trolls should be doing under L2 — the pair is
judged together. Example: "both trolls chop trees; one carries wood to our shack."

**L4 — Write the concrete moves.** The actual moves for the stuck turns in this exact position,
including the explicit non-oscillating resolution of the recorded episode. Example: "troll A
places its wood into the tent; troll B steps aside to (x,y) to clear the door, then returns to
its tree."

**Step 5 — Deviation analysis.** Only now open the code's view: what the bot actually did
(transcript; Decision Packet when available; the code-reference appendix for score mechanics).
Name the LEVEL at which the bot diverged — wrong state read (L1), wrong course (L2), wrong
joint behavior (L3), or right intent with a broken move (L4). This localization is what makes
34 rulings aggregate into a diagnosis.

**Step 6 — Rule candidates (the harvest).** Each ruling may propose one or more candidate rules
for `docs/RULES-LEDGER.md`, stated in game terms, with this situation as its first evidence.
The owner approves, edits, or rejects candidates at session end. A rule enters the ledger with
the list of situations that support it.

## Worked model case (the owner's example, session format)

- L1: middle phase; resources still on the map; two trolls each side.
- L2: our best course is to deny the opponent's camp.
- L3: both trolls chopping; one carries wood to our shack.
- L4: the carrier places wood into the tent; the second troll — currently blocking the
  carrier's way — steps aside to the named free square, then resumes its chop. No repeated
  squares; the episode resolves in two turns.
- Step 5: the bot instead recomputed a detour each turn and paced two squares for N turns —
  divergence at L4 (intent right, movement layer broken) [or as found].
- Step 6: candidate rule, e.g. "a troll whose current task can wait one turn yields the square
  a carrier needs" → proposed to the ledger with this situation attached.

## Status of the earlier material

- The v2 "goal-hierarchy doctrine" file is RETITLED as the **code-reference appendix**
  (`local_claude_1/code-reference-appendix-2026-08-15.md`): its Part 1 (C1–C9 + structural
  layer) is the verified description of what the code does, used ONLY in step 5. It defines
  nothing normative.
- Its Parts 2–3 (N-principles, T-tensions) are DEMOTED to a non-binding checklist a ruling MAY
  cite at L4/step 6 if genuinely relevant. They are candidates like any other; none is law
  unless it earns a ledger entry through rulings.
