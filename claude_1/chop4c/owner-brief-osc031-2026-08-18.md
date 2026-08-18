# Owner brief — which test kept saying "don't chop" in OSC-031

**Task 4c, `20260818-osc031-chop-clause-instrument`. This brief reports a measurement. It does
not tell you whether the answer is a bug or correct caution — that ruling is yours, and nothing
below is arranged to push it either way.**

## Your question

In recorded case OSC-031 a chop-capable troll, with trees on the board and no fruit to pick,
asked "should I chop?" every turn for 167 turns and answered **no** to every tree every time.
Which test inside the chop checklist said no? Nobody knew, and guessing was refused.

## The answer

**One test, every time.**

On all **167** of your locked turns, the chop planner performed **315** tree evaluations — it
asks the question more than once per turn — and **every single one of the 315** stopped at the
same test:

> **`PREDICT_TREE_NONE`** — the planner's *forecast* step. Before deciding whether a tree is
> worth chopping, the bot predicts what that tree will look like when the troll arrives. On these
> turns the forecast came back with **no tree to plan against**, so the checklist ended there.

Every other test in the checklist: **zero**. Not "rarely"; **never reached**, because the
forecast step is earlier in the list and stopped each evaluation before them.

| test in the chop checklist | times it was the deciding answer |
|---|---:|
| **`PREDICT_TREE_NONE`** (the forecast step) | **315** |
| capacity gate · reachability · predicted size/health · felling outcome · round-trip clock · wood · accept | **0** each |

## What was done so you can trust it

The bot itself was made to say its answer out loud — the real compiled bot, not a copy of its
arithmetic. The recorder was checked before its output was believed, and it took **five rounds
of review** to be accepted:

- the recorder logs **every** test it reaches, not just the one that said no;
- it produces **identical game output** to your untouched resident bot, so it is the same bot;
- the seven tests that show zero were each dealt with separately — **two were made to fire on
  purpose-built situations** (an unreachable tree; a turn-300 clock), and **three were proven
  incapable of firing** by running the bot's own arithmetic over **all 80,523,520 legal
  combinations**, including sabotage tests proving the prover notices violations when they exist;
- the list of 167 turns was **locked by the integrator in advance**, from last week's accepted
  measurements, and reproduced independently — nobody chose a flattering list after seeing the
  answer.

## The honest limits

- **This is one game.** Whether the same test dominates elsewhere is **not** measured here and is
  not claimed.
- **The 31 turns outside your list are reported, not hidden.** The instrument saw chop
  evaluations on 198 turns for that troll; 31 fall outside your locked population and are listed
  in the evidence file.
- **Why the forecast returned nothing is not part of this answer.** The measurement names the
  test that ended the checklist; it does not open up that test's internals.

## What is yours to decide

Whether a forecast step that returns nothing on these turns is **a defect worth a fix charter**,
or **correct caution the bot should keep**. Both readings are available on this evidence and I am
not recommending either.

Evidence: `claude_1/chop4c/g4c3-distribution-2026-08-18.json` (315 per-evaluation records with
self-checks) · `g4c3-clause-decision-table-2026-08-18.md` · manifest
`osc031-167-manifest.json`, sha256 `b9eed4c2…`.

Boundaries held throughout: no fix, no stamp, no class-wide claim, no Arena action; the resident
file is untouched.
