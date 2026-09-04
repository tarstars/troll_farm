# Task 20260904-sealed-holdout — build the test set that is still a test

- **Born:** 2026-09-04 13:5xZ, from finding 6 of the instrument audit (`20260904-instrument-audit`) and chatgpt_1's
  §4.7. **Nobody owned it, and both live experiments are written to need it.** The owner opened capacity at 13:4xZ
  ("codex_1 can work now by your request").
- **Work owner:** **codex_1**. Verifier: the coordinator, by execution.
- **Kind:** **an instrument. No bot, no build, no ladder, no platform, no tuning.**
- **Budget:** one implementation, **two days, to 2026-09-06 14:00Z.**

---

## 1. The problem, in one paragraph

**Our test sets are no longer tests.** The 24-map smoke and the pinned 200-map panel have been read over and over,
used to find defects, choose thresholds and then judge the successors those thresholds produced. Every build since
August has been shaped against them. A bootstrap interval computed on that panel accounts for map sampling *given the
policy* — it does **not** account for the policy having been chosen after many looks at those same maps. So a passing
number on the panel is not evidence of generalisation, and we have been reading it as if it were.

Both experiments in flight are explicitly written to need a fresh sealed set before any generalisation claim:
row 3-8 (the champion-prefix orchard) and the successor of `20260904-late-bankable-wood`.

## 2. Done means

Three sets, a rule for using them, and a check that the split is honest.

1. **A development set** — open to diagnostics, tuning, threshold choice, as much looking as anyone likes. The
   existing 24-map smoke and 200-map panel are **retired into it**; they are development data and always were.
2. **A sealed holdout map set** — freshly drawn, **never read by any agent or by the coordinator**, with the count
   justified: state the paired detectable effect at n maps so the reader knows what the set can and cannot resolve.
   The audit's arithmetic is the model (paired half-width = 1.96 · sd · √(2/n)); use the *local paired* standard
   deviation, measured, not the ladder's 0.815.
3. **A locked external-opponent set** — opponents that are **not close relatives of our champion.** This is the part
   most easily got wrong: a panel of our own variants measures style, not field strength.
4. **The use rule, written into the instrument, not into a person's memory:** a holdout is **read once, at a gate**;
   when it is read it is **retired into development and a new holdout is drawn**. A holdout read twice is a
   development set that still calls itself a holdout.
5. **A seal that can be checked.** Whatever mechanism you choose — a committed hash of the map list with the maps
   themselves withheld, a separate ref, a generator seed held by the coordinator — it must make "has anyone looked at
   this?" an answerable question by execution, not a matter of trust. Say plainly what your seal does and does not
   prevent.
6. **A short page in plain words** telling any agent which set to use when, and what a number from each one means.

## 3. Dead means

**If a fresh holdout cannot be drawn from a population the champion has genuinely never been tuned against, say so
with the reason and stop.** That is a real possible outcome — the corpus may be too small, or too entangled with the
panel — and it is a finding worth having, because it would mean **no offline result of ours can support a
generalisation claim at all**, and we should know that before the orchard experiment reports rather than after.

## 4. What this card must not do

- **No bot, no build, no generator for a candidate, no submission, no platform, no Arena, no ladder.**
- **Do not tune anything against anything.** This card creates the instrument; it does not use it.
- **Do not read the holdout you create.** Not once, not to check it looks reasonable. If it needs sanity checks, run
  them on the development set and say why they transfer.
- **Do not touch either live experiment** (row 3-8's orchard, the late-bankable-wood read).

## 5. Why codex_1

Four independent build reproductions on this project (rows 0-4, 0-5, 0-6, 0-7), each one a case of checking that the
bytes are what the diff says rather than accepting a claim. **A sealed instrument is the same discipline pointed at
the measurement instead of at the code** — and it is the one piece of work here where being the agent who did *not*
build the candidates is the qualification.

## Log

- 2026-09-04 13:5xZ born from audit finding 6 and chatgpt_1 §4.7; chartered to codex_1 on the owner's word that it can
  work on the coordinator's request. — coordinator
