# The four top players, reconstructed — the one page for the owner (2026-08-28, 03:50Z)

Your goal for the night: *"recover algorithms of 4 top players … a description of actions which is
enough for writing a program; all means are good."* The night shrank to two hours (the session stalled
from 19:50Z to 02:58Z), so the work ran as eight parallel workers between 03:00Z and 03:45Z. What exists
now, per player, is **`<player>/ALGORITHM.md`** — the algorithm in plain words, then pseudo-code, every
number with its source and n, every guess marked GUESS, every gap named — built on four legs: the public
write-ups (`sources/`), our own corpus profiles (`profiles/`), decision-rule fits on exact per-turn
states (`fits/`), and what the repository already knew (`prior-art.md`).

## Who they are (Legend ladder, 19:50Z) and what kind of program each is

| # | player | rating | kind of program | how much is solid |
|---|---|---|---|---|
| 1 | **delineate** | 30.89 | a **learned policy network** (ResNet trained by PPO, 101k parameters, one inference per troll + one for the "train plan", no lookahead, 2–3 ms a turn) — described first-hand by its author | HIGH on what it is; **no hand rules exist to copy** — only its action/target spaces, observation, training curriculum and measured habits (a rule-based imitation is written in its document) |
| 2 | **norxondor_gorgonax** | 29.66 | a **fast rule-based 3–4-troll build-up bot**: its own telemetry reads 0.13 ms a turn — no search; a global two-phase state machine (P = produce, D = deforest) — the author never wrote anything | MEDIUM-HIGH: the train ladder is exact (441/443 specs), the phase switch, the planting cell, the lifecycle and the roles are measured; the target choice and the plant kind are not |
| 3 | **Bubaptik** | 27.90 | a **3–4-troll build-up bot with speed-4 choppers**; not in the contest's top league (probably a later entrant), no trace on the web | MEDIUM: 191 games of its newest version (34 versions in the corpus); the train rule is exact (147/154), the wood switch is a hard global switch at its last TRAIN; target choices fitted 44–56 %, mid/late chop not recovered |
| 4 | **MSz** | 27.72 | a **"farm-first" build-up bot**: an instant cheap worker on turn 1 (an exact rule), a two-ring orchard, then two carry-4 lumberjacks paid with lemons, fruit harvested all game — no Troll Farm write-up; his search is a GUESS from his other post-mortems | MEDIUM: lifecycle, ladder, funding sequence and roles measured; search, evaluation and target choice unknown |

Our champion (yamo's design, #3 in the contest) is the other family — **two trolls**, one trained ≈ 2/2/0/2
chopper, chop everything, no orchard. The contest's top ten splits into exactly these two families.

## What all four do that we do not (the facts that survive every leg)

1. **They grow trolls 3 and 4, and pay for them with an orchard planted next to the shack.** delineate
   ends with 2.9 trolls (a third in 56 % of games at median turn 111, a fourth in 27 % at 144, winning
   91 % of the games where it has four); norxondor 3.5 (four or more in 52 %; ladder floors 2/2/1/1 →
   2/3/1/2 → 2/3/0/3 → 2/4/0/3 by roster size, each talent raised to the most the shack can pay, with
   caps); MSz trains on **turn 1** in 214 of 215 games by an exact rule (speed 2 iff plums ≥ 5, carry 2
   iff lemons ≥ 5, harvest 2 iff apples ≥ 5, chop 1), then carry-4 trolls at ≈97 and ≈128; Bubaptik on
   turn 2 (each talent = the highest level the starting stock affords, 147/154), then **speed-4**
   trolls 4/3/h/2–3 at ≈115, ≈150, ≈164. **The training trigger is the same in all four: train within a turn of
   the target becoming affordable** (delay 0 or 1 in 88–99 % of trainings; delineate the same turn in
   61 %). The late trolls are carry-3/4, chop-2/3 lumberjacks with little or no harvest power; carry 4
   costs 16+n lemons, speed 4 costs 16+n plums — hence the orchard.
2. **They plant next to the shack, 29–40 trees a game** (delineate 40 — lemons first, bananas after
   turn 100; norxondor lemon 35 % / plum 32 % / banana 26 %, never beyond distance 4; MSz a two-ring
   orchard within distance 2 in 91 % of plants, apples next to water; Bubaptik plums for the speed-4
   bills). One rule fits the planting cell everywhere: **the free cell minimising distance-to-shack plus
   distance-to-the-troll** (78–90 % of all plants; MSz 77.6 %). Our champion plants 10 a game, 82 % after turn 250.
3. **The game has two phases, and the switch is explicit.** norxondor's P→D switch (median turn 153,
   one turn after its last TRAIN in 62 % of games): only 7 chops in the first 100 turns, first wood at
   median turn 97, then the highest chop rate on the ladder and a clear-cut tied to the fourth troll.
   Bubaptik: a hard global switch at its **last TRAIN** (chops per turn 0.03 → 0.69, mining stops,
   bananas picked from the shack as the quick crop). MSz: first wood ≈116, chops least and latest,
   78 % near its own shack, and keeps harvesting to the end (78 fruit points a game; the only apple
   farmer). delineate: no switch, its chop rate simply rises with the roster.
4. **The wood comes from their own trees.** norxondor's signature is **plant-and-cut bananas** — a
   banana planted on the shack-adjacent cell and felled at size 1 the next turn (1 fruit point → 4 wood
   points; 1,116 bananas cut at size 1, and 2,407 own-tree cuts within four turns of planting, in 184
   games). delineate's and Bubaptik's first wood comes early (median turn 24–26) from raids; norxondor's
   and MSz's late (turn 97 and 116) from their own trees. delineate chops 172 times a game: the first 50 turns on the
   opponent's half (56 % within two cells of their shack — a nursery raid), the last 50 on its own banana
   farm at size 4. MSz cuts its own trees grown to full size (median age 26–37 turns). Bubaptik's early
   chops are denial (50 % on the opponent's trees), late ones 70 % its own.
5. **Movement is step-wise** in three of the four (delineate, norxondor, MSz issue MOVEs one to three
   cells at a time; the destination is invisible); Bubaptik moves destination-style.
6. **No simple formula explains the chop-target choice of any of them.** Our champion's value rule
   (wood per turn of the trip) predicts 20–42 % of their targets; the best rules 25–63 %; the repo's
   earlier norxondor ranker reached 41.8 %. What the data supports instead: phases, roles (the starter
   farms at the shack, the chop-3 trolls only chop), denial and co-chop biases. This is the largest open
   gap for "writing a program" — and the per-player documents say so.

## What is solid, what is not — plainly

- **Solid:** delineate's architecture and training recipe (its own words); every player's training
  ladder and trigger, planting cell, lifecycle by turn, phase switch, roles, score composition (our
  corpus, exact states, n = 182–223 games each, validated against the referee's own tallies); the
  family write-ups that describe the build-up mechanics (wala, laconic_pixel, xSkyline, aangairbender,
  FinkPloyd, eulerscheZahl, Astrobytes).
- **Not solid:** the target-selection rules (chop; the plant kind) of all four; norxondor's tie-breaks
  and the meaning of its second message letter; MSz's search and evaluation; Bubaptik's roster cap and
  speed-1 fallback trigger; anything about older versions.
- **A warning from our own history** (`prior-art.md`): the one time a norxondor-shaped controller was
  built from fitted rules it lost by −173 points closed-loop despite matching 77 % of its recorded decisions — a training
  ladder without its funding mechanism is inert (−170). What makes a third troll affordable is both
  workers collecting one bill together (+106 in that study) — norxondor's P mode is exactly that.
  A program built from these documents must be judged on real maps, never on per-decision accuracy.

## The nearest ideas to test on our champion (one variable each, in order)

1. **The funding coalition for a third troll**: after the second troll, both trolls collect one bill
   (lemons first: carry 3–4 costs 10–17 lemons) and train a carry-3/chop-3/harvest-0 lumberjack the turn
   it becomes affordable (the exact trigger the top four use). Evidence: all four; the repo's +106.
2. **The orchard rule while funding**: plant lemons/plums from turn 1 on the free cell minimising
   distance-to-shack + distance-to-troll, never beyond distance 4; bananas after turn ~100. Evidence:
   78–90 % of 20,000+ plants.
3. **The explicit two-phase switch**: produce until the last planned troll is trained, then deforest —
   every troll chops, no more mining or training (norxondor, Bubaptik). Evidence: measured switch.
4. **Plant-and-cut bananas** on the shack-adjacent cell in the deforest phase (1 point → 4).
   Evidence: 1,116 size-1 cuts.
5. **The early raid**: in the first 50 turns, chop the opponent's freshly planted trees near their
   shack (delineate 56 %, Bubaptik 50 % of early targets). Evidence: measured; the mechanism guessed.

Everything here is measurement; none of it is a verdict. The per-player documents carry the numbers,
the pseudo-code and the guesses; they were written by four workers in parallel and read by the
coordinator only at the level of their reports — a second pair of eyes is welcome.

## Files

- `PLAN.md` — the night's plan. `README.md` — this page.
- `delineate/ALGORITHM.md` (4.6k words), `norxondor_gorgonax/ALGORITHM.md` (5.3k), `Bubaptik/ALGORITHM.md`
  (4.5k, + `train_trigger.py`/`.json`, `plan_end.py`/`.json`), `MSz/ALGORITHM.md` (4.8k).
- `sources/` — 26 files: the write-ups verbatim, the game author's statistics for 69 Legend players, the
  contest threads, the rules; `sources/SUMMARY.md` is the digest.
- `profiles/` — `profile_bot.py` + six profiles (the four, tass, yamo) + `COMPARISON.md`: exact positions
  and tree origins from the referee's per-turn log inside the raw replays.
- `fits/` — `reconstruct.py` (exact states: engine replay + keyframe diff, 0 disagreements on 784 games),
  `decision_tables.py`, `fit_rules.py`, per-player fit reports and decision tables.
- `prior-art.md` — what the repository already knew (norxondor's ladder, delineate's first-troll rule,
  the 21 imitation closures, the tools).
