# The four top players, reconstructed — the one page for the owner (2026-08-28, ~04:00Z)

Your goal for the night: *"recover algorithms of 4 top players … a description of actions which is
enough for writing a program; all means are good."* The night shrank to two hours (the session stalled
from 19:50Z to 02:58Z), so the work ran as seven parallel workers between 03:00Z and 04:45Z. What exists
now, per player, is `<player>/ALGORITHM.md` (the algorithm in plain words, then pseudo-code, every number
with its source, every guess marked), built from four legs: the public write-ups (`sources/`), our own
corpus profiles (`profiles/`), decision-rule fits on exact per-turn states (`fits/`), and what the repo
already knew (`prior-art.md`).

## Who they are (Legend ladder, 19:50Z) and what kind of program each is

| # | player | rating | kind of program | how much is solid |
|---|---|---|---|---|
| 1 | **delineate** | 30.89 | a **learned policy network** (ResNet trained by PPO, 101k parameters, one inference per troll + one for the "train plan", no lookahead) — described first-hand by the author | HIGH on what it is; there are **no hand rules to copy**, only its action/target spaces, observation, curriculum and measured habits |
| 2 | **norxondor_gorgonax** | 29.66 | a **3–4-troll build-up economy**, search-based (GUESS: prints timing telemetry every turn, non-deterministic) — the author never wrote anything | MEDIUM: its training ladder, planting cell and lifecycle are measured exactly; its target choice is not |
| 3 | **Bubaptik** | 27.90 | a **3–4-troll build-up economy** with speed-4 lumberjacks — a post-contest entrant, no trace on the web | MEDIUM-LOW: only our corpus (191 games of its newest version) |
| 4 | **MSz** | 27.72 | a **"farm-first" build-up economy**: an instant cheap worker, then two carry-4 lumberjacks, fruit all game — no Troll Farm write-up (his other post-mortems: exact engine + beam/hill-climb + Hungarian assignment, a GUESS for this game) | MEDIUM: measured lifecycle and ladder; search and evaluation unknown |

Our champion (yamo's design, #3 in the contest) is the other family: **two trolls**, one trained ≈ 2/2/0/2
chopper, chop everything, no farm. The whole top-10 of the contest splits into these two families.

## What all four do that we do not (the facts that survive every leg)

1. **They grow trolls 3 and 4, paid by an orchard planted next to the shack.** delineate ends with
   2.9 trolls (a third in 56 % of games at median turn 111, a fourth in 27 % at 144 — and wins 91 % of
   the games where it has four); norxondor 3.5 (four or more in 52 %; ladder 2/2/2/2 at turn ≈9 →
   2/3/1/2 at ≈100 → 2/3/0/3 at ≈132 → 2/4/0/3 at ≈153); MSz trains on **turn 1** in 214 of 215 games
   (the cheapest harvest-capable troll the starting stock allows), then carry-4 trolls at ≈95 and ≈129;
   Bubaptik trains on turn 2 in 89 % of games, then **speed-4** trolls (4/3/x/2–3 at ≈118, 4/3/1/3 at ≈153).
   The training trigger is exact in all four: **train the turn the target becomes affordable** (delay 0
   in 88–99 % of trainings). The late trolls are carry-3/4, chop-3, harvest-0 lumberjacks.
2. **They plant next to the shack, a lot: 30–40 trees a game** (delineate 40, mostly lemons first and
   bananas later; norxondor lemon 35 % / plum 32 % / banana 26 %, never beyond distance 4; MSz a
   two-ring orchard within distance 2 in 91 % of plants, apples next to water; Bubaptik plums). The
   planting cell obeys one rule everywhere: **the cell that minimises distance-to-shack plus
   distance-to-the-troll** (84–90 % of all plants). Our champion plants 10 a game, 82 % of them after
   turn 250.
3. **The wood comes from their own trees, late.** norxondor: only 7 chops in the first 100 turns, first
   wood at median turn 97, then the highest chop rate on the ladder (12–13 per 10 turns) and a clear-cut
   from turn ~150–175 tied to the fourth troll; its signature is **plant-and-cut bananas** — a banana
   planted on the shack-adjacent cell and felled at size 1 the next turn (1 fruit point → 4 wood points;
   2,407 such cuts in 184 games). delineate chops 172 times a game: the first 50 turns on the opponent's
   half (56 % within two cells of their shack — a raider), the last 50 on its own banana farm. MSz chops
   least (118) and latest (first wood ≈116), 78 % near its own shack, and keeps harvesting to the end
   (78 fruit points a game, apples included — the only apple farmer).
4. **Movement is step-wise** (delineate, norxondor, MSz issue MOVEs one to three cells at a time; the
   destination is invisible) — a sign of pathing inside a search or a policy, not "MOVE to the target".
5. **No simple formula explains their chop-target choice.** Our champion's value rule (wood per turn of
   the trip) predicts 20–42 % of their targets; the best positional rules 25–63 %; the repo's earlier
   norxondor ranker reached 41.8 %. What the data supports instead is a phase structure (raid → farm →
   clear-cut) and per-troll roles. This is the largest open gap for "writing a program".

## What is solid, what is not — plainly

- **Solid:** delineate's architecture and training recipe (its own words); every player's training
  ladder and trigger, planting cell, lifecycle by turn, roles, score composition (our corpus, exact
  states, n = 182–223 games each); the family write-ups that describe the build-up mechanics in detail
  (wala, laconic_pixel, xSkyline, aangairbender, FinkPloyd, eulerscheZahl, Astrobytes).
- **Not solid:** the target-selection rules (chop, and the plant kind) of all four; the search each
  hand-written bot runs (norxondor and MSz almost surely search; depth and evaluation unknown); anything
  about Bubaptik beyond its habits.
- **A warning from our own history** (`prior-art.md`): the one time a norxondor-shaped controller was
  built from fitted rules it lost by −173 points closed-loop despite 77 % move accuracy — a training
  ladder without its funding mechanism is inert. The mechanism that makes a third troll affordable is a
  temporary coalition of both workers on the bill (+106 in that study), and it is the thing to copy first.

## The nearest ideas to test on our champion (one variable each, in order)

1. **The funding coalition for a third troll**: after the second troll, both trolls collect one bill
   (lemons first: carry 3–4 costs 10–17 lemons) and train a carry-3/chop-3/harvest-0 lumberjack when it
   becomes affordable (the exact trigger the top four use). Evidence: all four; the repo's +106.
2. **The orchard rule**: plant lemons/plums on the cell minimising distance-to-shack + distance-to-troll
   from turn 1 while funding, bananas after turn ~100; never beyond distance 4. Evidence: 84–90 %.
3. **Plant-and-cut bananas** on the shack-adjacent cell as the endgame conversion (norxondor's
   signature, 1 point → 4). Evidence: 2,407 cuts.
4. **The early raid**: in the first 50 turns, chop the opponent's freshly planted trees near their
   shack (delineate 56 % of early targets there; Bubaptik 50 %). Evidence: measured, mechanism guessed.

Everything here is measurement; none of it is a verdict. The per-player documents carry the numbers,
the pseudo-code and the guesses.

## Files

- `PLAN.md` — the night's plan. `README.md` — this page.
- `delineate/ALGORITHM.md`, `norxondor_gorgonax/ALGORITHM.md`, `Bubaptik/ALGORITHM.md`, `MSz/ALGORITHM.md`.
- `sources/` — 26 files: the write-ups verbatim, the game author's statistics for 69 Legend players, the
  contest threads, the rules; `sources/SUMMARY.md` is the digest.
- `profiles/` — `profile_bot.py` + six profiles (the four, tass, yamo) + `COMPARISON.md`.
- `fits/` — `reconstruct.py` (exact states: engine replay + keyframe diff, 0 disagreements on 784 games),
  `decision_tables.py`, `fit_rules.py`, per-player fit reports and tables.
- `prior-art.md` — what the repository already knew (the norxondor ladder, delineate's first-troll rule,
  the 21 imitation closures, the tools).
