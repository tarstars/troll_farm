# GOALS — what we are trying to achieve, and how far along we are

Owner-facing. Plain words, every number tied to a dated measurement. Three goals, one number each.
Hard budget 60 lines, enforced by `tests/test_doc_budgets.py`. Last updated 2026-08-23.

## G1 — Find out whether the problems we keep fixing are real

Everything we repaired was chosen from **34 hand-picked situations** on a since-retired bot, picked
*because* something had gone wrong in them. We never checked whether they happen in real games.
Meanwhile the ladder says two generations of those repairs are worth **+0.17** — near nothing.

- **Measure:** our own real ladder games graded for dancing, contention and repeated pick-and-drop,
  **with the bot's own stated intention attached to every turn**.
- **Now: 149 games** (0 → 149 on 2026-08-23), 38,869 of our turns, 0 refused — graded for dancing and
  contention, **and the intentions are joined**: 76,305 turn×unit rows, decoder independently
  accepted, 12/12 controls. Idleness is the one problem still ungraded. **Target: 500.**
- **First result**, at **matched own-unit count** — contention scales with unit count, so nothing
  else is a fair comparison. Share of games showing the defect:
  **contention — us 0 % of 149; the opponents in those same games 23 %; our pre-cure bot 43 %.**
  **Dancing — us 11 %, those opponents 14 %, our pre-cure bot 0 %.** The defect two generations of
  work targeted is **gone from real play**; **dancing is the one that survived**, and we now do it
  more than our predecessor did. Rows: `local_claude_1/narrate/g1-first-grading-2026-08-23.json`.
- **Limits:** different eras, so not randomised; the zero is not attributable to any one cure; replay
  dancing counts are an **upper bound** (reconstructed plant clocks invent dancing) applied
  identically to every cohort; 149 games is one agent, mid-maturation.

## G2 — A settled ladder score of 25.40 or better

25.40 is the boundary of the top ten. *Settled* means a score that has stopped drifting, confirmed a
second time — never a single good reading.

- **Now: 22.6** (champion `547fa706`, one reading, 2026-08-23). **Target: 25.40, confirmed twice.**
- **In the way:** we do not know what would add three points. Fixing more individual defects has
  been measured and it does not do it. **G1 exists to find out what would.**

## G3 — The system runs a working day without the owner

Agents work until a decision genuinely needs the owner, against a board whose progress is visible.

- **PAUSED by the owner 2026-08-23** — *"important, but I think we are to make a special focus on
  it"*. Deferred to a session of its own: not dropped, and not worked at in the margins of other
  tasks. Nothing is owed and no decision about it is raised until then.
- **Measure:** longest stretch of useful work with no owner input. **Now: minutes. Target: 8 h.**
- **What that session must solve:** almost every job is released by a coordinator ruling, and the
  coordinator has no clock. **Pausing is cheap** — runs advance more slowly, and the resident bot
  keeps playing real games meanwhile, which is what G1 wants anyway.

## How this file is kept honest

1. **Every number comes from a measurement, with a date and a source** — never from memory. This
   project has published false figures from recall more than once.
2. **A number that cannot be measured today says so**, rather than being estimated.
3. **No rate without its control.** An "N of N" never tested against a deliberately wrong pairing
   describes the sample, not the world; two such figures were withdrawn on 2026-08-23. A **zero** is
   only reported once the detector has been shown able to fire.
4. **Updated when a number changes**, not on a schedule.

## What needs the owner right now

**Nothing.** When something does it appears here and in `docs/STATE.md` §4.
