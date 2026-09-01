# The harness — how to run your bot against the reference bot

Three things live here:

- **`reference-bot`** — the bot you are trying to match, as a compiled executable. There is no
  source for it in this package and there will not be. It reads the protocol of RULES §13 on
  standard input and writes one line of commands per turn to standard output.
- **`maps/`** — 24 frozen starting positions, six of each map size (16x8, 18x9, 20x10, 22x11).
  They are the real starting states of 24 recorded ranked matches, not generated ones, so every
  position here is one the platform actually dealt. Each is a JSON file: the map rows, both
  players' starting stock, every tree with its exact size, health, fruit count and cooldown, and
  both starting trolls.
- **`referee.py`** — a referee, and a runner that starts two programs as child processes, speaks
  the protocol to both, applies the rules, and reports the result.

## Running it

    python3 referee.py --p0 ./reference-bot --p1 "python3 mybot.py"
    python3 referee.py --p0 ./reference-bot --p1 ./mybot --both-seats --json results.json

`--both-seats` plays every map twice, swapping which program sits in which seat. Always use it
for anything you intend to draw a conclusion from: the map is symmetric but the two seats are not
interchangeable in the referee's resolution order.

Useful flags: `--limit N` (first N maps only), `--turns N` (shorter matches while debugging),
`--enforce-time` (lose on the third overrun, as the platform does; off by default so a debugger
does not lose you the match).

## Two ways this referee differs from the platform's, on purpose

1. **Equal-best movement ties.** The platform's referee breaks a tie between two equally short
   steps **randomly**; this one takes the lexicographically smaller cell (RULES §4). A bot whose
   play depends on which of two equal steps it gets is a bot that will behave differently on the
   platform. Do not tune against this.
2. **Time is measured but not enforced** unless you pass `--enforce-time`. The numbers it
   measures are *this machine's*, and this machine is not the judge machine
   (CONSTRAINTS §3).

Everything else is the rules as written in `RULES.md`. If you find a disagreement between
`referee.py` and `RULES.md`, that is a bug in the package — say so.

## The acceptance ladder

Climb it in order. Do not read a number from a later step until the earlier one is clean.

**Step 1 — legal, complete matches.** Play all 24 maps, both seats (48 matches):

    python3 referee.py --p0 ./reference-bot --p1 ./mybot --both-seats --json step1.json

Pass = **48 of 48 finished with no illegal command and no crash** (the runner prints how many
ended that way, and exits non-zero if any did). Ignore the scores entirely at this step. A bot
that scores well and crashes in one match in fifty is not ready; fix the crash first.

**Step 2 — the scout, 48 matches.** The same 48 matches, now read for strength. This is a look,
not a verdict: 48 matches is enough to see a bot that is far off and not enough to separate two
close ones. What you want here is a win count that is not embarrassing and a mean margin that is
not a collapse.

**Step 3 — the locked panel, 144 cells.** 24 maps x 2 seats x 3 repeats = 144 matches, run once,
with the map list and the command lines **written down before you run it**. The point of locking
it is that you cannot go back and choose a different panel after seeing the result. Compare per
cell — the same map and seat, your bot and the reference — and report the **paired** margin, not
two separate averages.

**Step 4 — 400 matches.** Only if step 3 says it is close. Parity means the 95 % interval of the
per-cell margin difference contains zero or better.

## What "the same strength" means here

The reference bot's own scores on these maps are in the range 120–220 with a mean near 180, and
against itself it wins about half the time. If your bot loses 48 out of 48 you have a bug, not a
strategy problem. If it wins 30 of 48 you have something; take it to step 3 before believing it.

## A caution about this harness as a judge

These 24 maps and one opponent are not the ladder. A local result has been wrong about the real
ladder by a wide margin more than once on this project (`DOMAIN.md` §4). Treat the harness as a
check that your bot **works** and is **roughly in the right class**, and treat a small local
advantage as noise.
