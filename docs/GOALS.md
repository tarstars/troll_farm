# GOALS — what we are trying to achieve, and how far along we are

Owner-facing. Plain words, every number tied to a measurement with a date. Three goals, each with
one number you can watch move. Hard budget: 60 lines, enforced by `tests/test_doc_budgets.py`.

Last updated: 2026-08-23.

## G1 — Find out whether the problems we keep fixing are real

Everything we have repaired was chosen from **34 hand-picked situations**, recorded on a bot we have
since retired, and picked *because* something had gone wrong in them. We have never checked whether
those situations happen in real games, or how often. Meanwhile the ladder says two generations of
those repairs are worth **+0.17** — near enough to nothing.

- **Measure:** how many of our own real ladder games we have graded for the three known problems —
  trolls dancing on the spot, trolls blocking each other, trolls standing idle — **with the bot's
  own stated intention attached to every turn**.
- **Now: 0 games.** **Target: 500.**
- **Moving it:** the bot now says out loud what each troll is aiming at, every turn, and the platform
  records it. It is on the ladder as submission `41182039` and collecting.
- **In the way:** nothing.

## G2 — A settled ladder score of 25.40 or better

25.40 is the boundary of the top ten. *Settled* means a score that has stopped drifting, confirmed a
second time — never a single good reading.

- **Now: 22.6** (champion `547fa706`, one reading, 2026-08-23). **Target: 25.40, confirmed twice.**
- **In the way:** we do not know what would add three points. Fixing more individual defects has
  been measured and it does not do it. **G1 exists to find out what would.**

## G3 — The system runs a working day without the owner

Agents should keep working until a decision genuinely needs the owner's judgment, against a visible
board, with progress you can see without asking.

- **Measure:** the longest stretch of useful work with no owner input.
- **Now: minutes.** **Target: 8 hours.**
- **In the way:** two things, both structural. Nearly every job's release condition is *"a written
  ruling from local_claude_1"*, so the coordinator is the bottleneck by design. And the coordinator
  has no clock — it exists only while the owner is typing. The autonomous workers (`claude_1`,
  `codex_1`) do run unattended, but they are woken by mail and may not touch the Arena.

## How this file is kept honest

1. **Every number comes from a measurement, with a date and a source.** Never from memory. This
   project has published false figures from recall more than once.
2. **A number that cannot be measured today says so**, rather than being estimated.
3. **A rate is not reported without its control.** A "100 %" or an "N of N" that has never been
   tested against a deliberately wrong pairing is a description of the sample, not a finding. Two
   such figures were withdrawn on 2026-08-23.
4. **Updated when a number changes**, not on a schedule.

## What needs the owner right now

**Nothing.** When something does, it appears here and in `docs/STATE.md` §4, and nowhere else needs
to be read to find it.
