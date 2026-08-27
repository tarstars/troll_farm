# Morning brief — the night of 2026-08-26/27 (for the owner, plain words)

Written at 05:30Z while the measurement runs. The board is `coordination/BOARD.md`; the hour-by-hour
log is `local_claude_1/goal-log-2026-08-26.md`. Two bots and I worked through the night; nothing
was submitted to the platform except the planned measurement steps.

## 1. The measurement of the "cured dancing troll" — five of sixteen readings

Two versions of our bot take turns on the ladder, each one printing per-turn diagnostics that come
back with the collected games:

- **A — the champion** (unchanged behaviour): **21.8, 21.6, 22.1** → mean **21.83**, best rank 37.
- **B — the champion plus "a troll keeps its goal"**: **18.4, 19.2** → mean **18.80**, ranks 82 and 68.

**The gap is about 3 points and the two sets do not overlap** — every B reading is below every A
reading. Three more readings each are due through the morning. If it holds, the plain reading is
that the keep-your-goal rule costs roughly three ladder points, which matches the local bench's
sign (it predicted a small loss) but is far larger than the bench's size. Nothing is decided: no
promotion, no revert, and the champion stays the champion by default.

## 2. The banana wood farm — built, and stopped by its own safety check

It went from your outline to a running arm in one evening: contract → design (two review rounds) →
build → one local test run. Then it stopped itself:

- **Games where a troll gets stuck rose from 52 to 96** out of 240. On 35 of the 50 new ones the
  cause is the opponent walking onto our hut ring and **harvesting the fruit we grew**.
- **The stop-latch never fired** — not once in 240 games — because it counts the enemy *chopping*
  our ring trees, while the theft that actually happens is *harvesting*. One design defect, showing
  up twice.
- On the local bench its own score was **+3,100 over 240 games** — the opposite sign to what we
  expected — but under a failed safety check that number buys nothing.
- codex_1 reproduced the failure exactly from the pushed commit. **Nothing was submitted; the
  queued platform slot was released.**

**Your decision:** a bounded repair (the latch must count harvests, not chops; the placement must
not hand the enemy a standing crop) — or close the line. The obituary in `coordination/GRAVEYARD.md`
states both requirements; no repair work has been started.

**The code to read:** `readable/diffs/banana-farm-vs-v6-instrument.diff` — 887 added lines, the farm
rule and its telemetry alone. (There is also a 1,811-line `banana-farm.diff` against the plain
champion; claude_1 published both and warned that the big one is misleading on its own, because it
carries the earlier candidate's machinery switched off. Read the small one.)

## 3. Two instruments finished, and one myth removed

- **The diagnostics survive the platform.** Our new resident prints a ~290-character line every
  turn — more than twice anything we had ever collected. Tonight's collection brought 287 of our
  games: **78,424 diagnostic lines, 242–295 characters, zero decode failures, no truncation.** Real
  ladder games now carry each troll's goal and why it kept or released it.
- **Fixtures are generated again, not frozen.** The 34 old test situations were retired yesterday
  (they were an ancient bot's episodes). `scripts/cut_fixtures.py` now cuts situations out of real
  instrumented games and tags them with the bot that produced them; the first two libraries are on
  `main` (champion 56,288 rows, keep-rule bot 1,200 rows). The keep-rule sample is thin — four
  games — and a second slice can be shipped on your word.

## 4. Housekeeping

The peer branches are integrated into `main` at every gate (the farm packet, the diffs, the
generator, the libraries all landed overnight). Two transport faults — messages pinned to commits
that their own author's rebase had erased — were quarantined so everyone's mail keeps working; the
rule is now "rebase first, publish the pinned handoff after". My own mistakes are in the log: a
commit written in the wrong checkout, the collector's statistics file discarded while repairing it
(the corpus itself is intact and the file regenerates nightly), a decoder check that first reported
failures which were my own harness, and a cleanup command whose pattern was too broad — caught and
restored in the same minute.

## 5. What is waiting for you

1. **The farm:** bounded repair, or close the line.
2. **When the measurement ends** (about eight more hours of alternating reads): what to do about
   the keep-your-goal rule, given a ~3-point ladder cost.
3. Optional: a second replay slice so the keep-rule fixture library is more than four games.
