# yannbot — reproduction of Yann Moisan's #3-Legend Troll Farm bot

**Status: DRAFT — pending user approval** (purpose defaulted to "champion candidate +
sparring" per controller recommendation while user AFK; revisit on review).
Source: `docs/reference/yann-moisan-postmortem-2026-05-26.txt` (archived verbatim from
yannmoisan.com, postmortem dated 2026-05-26; **#3 Legend / 2022, Scala, 2 trolls, no farm**).

## Why (strategic context)
- Rethink directions #3/#4 (docs/strategic-rethink-2026-07-11.md): copy demonstrated
  top-tier play instead of inventing. This is the strongest publicly documented build.
- It refutes "4-troll or bust": #3 Legend = 2 trolls + superb chop targeting + training
  DENIAL + game-end control. Our champion is already 2-troll — the gap is targeting/denial/
  endgame, all execution-class (the only class that has ever transferred).
- A faithful yannbot is ALSO the diverse sparring opponent the failed abgate calibration
  says head-to-head lacks (spec 2026-07-11-selfplay-gate-design.md, DIAGNOSIS).

## Verified referee facts this design relies on (checked 2026-07-11)
- `Player.recomputeScore` (referee master) = banked PLUM+LEMON+APPLE+BANANA + WOOD_POINTS·WOOD.
  **No planted-tree scoring** — our engine's scoring is CORRECT.
- The postmortem's "minor rule change" = referee commits 293d185 (May 13, "balancing:
  increase shack distance") and d821ba2 (May 25, "multiplayer changes: game end condition…").
- ⚠ WORK ITEM E1: our engine/driver end a game when `plants.is_empty()`. The May-25 commit
  changed the END CONDITION — read the referee's current end-of-game logic and align
  engine + driver if they differ. Yann's endgame (plant-to-extend when behind; contest
  opponent plants when ahead) only makes sense against the real end condition, and this
  affects ALL our local measurement, not just yannbot.

## The bot (faithful core, from the postmortem)
1. **Phase 1 — fund the strongest second troll fast.** Cost/stat (our verified formula,
   troll 2): stat 2 = 5, stat 3 = 10, paid PLUM→ms, LEMON→cc, IRON→chop; hp fixed at 1
   (2 apples, covered by starting inventory). Choose the strongest spec reachable quickly:
   estimate time-to-threshold from round-trip distances to the nearest fruit source of each
   needed type / iron cell; train the moment affordable.
2. **Main loop — candidate generator per troll:**
   - DROP at shack: score 8000 (carrying, adjacent).
   - MOVE toward shack: 7000 (carry full).
   - Chop / move-to-tree: dynamic `value = min(arrivalSize, carryRemaining) /
     (travelTurns + chopTurns + returnTurns)` (ceil for fractional turns), where
     arrivalSize/health come from **tree simulation** `nextN(travelTurns, oppChop)` over our
     engine's tree model (growth ticks + opponent chopping); SKIP trees that die before
     arrival. Opponent chop power: taken directly from protocol input (deviation from his
     isDamaged inference — we have the field; same information, simpler).
3. **typeToCut (turn 1):** LEMON or PLUM, whichever type's cluster is closer (summed BFS
   distances from our shack over all trees of that type). While the opponent has ≤2 trolls,
   typeToCut trees use an ALTERNATIVE scoring that rewards proximity to the OPPONENT's
   shack (training denial — lemon/plum are their training currency).
4. **Coordination:** enumerate candidate pairs (a,b), forbid same target cell (tree/harvest/
   drop), pick max combined score. n=2 → exact and trivial.
5. **Endgame** (turn > 250, OR trees nearly gone AND we are behind): bank-rush all carry;
   PICK banked fruit and PLANT on empty cells to EXTEND the game (behind) — planting spends
   1 banked point to keep the game alive for wood catch-up; when AHEAD, park adjacent to the
   opponent's shack to contest their extension plants.
6. **v1.0 stays faithful to his admitted weaknesses:** naive movement (destination only, no
   joint move solver), no sweet-spot planting, no mid-game fruit harvesting beyond funding.
   These are the study baseline. **v1.1 (separate, measured):** swap in our joint move
   solver — playmatch measures the delta. Nothing else hybridized until v1.0 is measured.

## Reproduction gaps (postmortem under-specifies; resolve by MEASUREMENT, never guessing)
G1: the denial scoring formula (concept only) — parameterize (e.g. weight × proximity-to-opp-
    shack term), sweep 2-3 values via playmatch vs ringfix3 + boss gate.
G2: "strongest second troll" tie-break between reachable spec tiers (3.3.1.3 vs mixed) and
    the time-vs-strength tradeoff constant — sweep.
G3: "trees almost gone" endgame threshold — start with (fellable trees ≤ 2) — sweep.
G4: whether typeToCut clusters count all sizes — start all-trees-of-type.
G5: funding-phase harvest specifics (which fruit first) — nearest-needed-type greedy.

## Architecture & packaging
- New isolated module `rust/src/botmain/yann.rs`: `pub fn decide_yann(state, mem) -> String`
  (own memory struct; NO reads of the champion's bands/planner). Dispatch: a top-level
  `const DECIDER` in main.rs selects elite (default) vs yann; champion path proven untouched
  by the equality harness (elite build vs pre-change binary, 25 seeds EQUAL).
- Artifacts: `yannbot` sparring binary (bundle with DECIDER=yann → rustc) registered as a
  gate opponent; submission artifact `cgauto/submissions/y1.0.0-yannrepro.min.rs` via the
  standard bundle→minify→MIN-OK pipeline (≤100KB).
- Branch: stacks on `abgate-selfplay-gate` (needs playmatch/abgate for all measurement).

## Validation plan (in order; each recorded in the silver log)
V1: component tests (funding math incl. 5/10 thresholds; throughput valuation with arrival
    simulation vs hand-computed fixtures; pair dedup; endgame triggers).
V2: full-game legality: plays 300-turn games vs WAIT and vs ringfix3 via playmatch without
    crashes/illegal commands; deterministic (abgate --selftest yannbot = exact zeros).
V3: playmatch yannbot vs ringfix3, n=200 both seats — the first DIFFERENT-strategy matchup
    for the gate (more informative than sibling mirrors; still not the arena).
V4: boss gate (8-12 real Boss-5 games) — Yann's shape (3.3.1.3-class chopper) is closest to
    Boss 5's own; expect the most honest local read here.
V5: arena, chained on ringfix3 per policy v2, ONLY if V3+V4 are non-negative — else it
    stays a sparring opponent (still a full success for purpose #2).

## Success criteria
1. v1.0 faithful core passes V1+V2. 2. V3+V4 verdicts recorded either way. 3. yannbot
registered as a standing gate opponent (fixes the calibration blind spot with a genuinely
different strategy). 4. E1 (end-condition fidelity) resolved in the engine. 5. Champion
path equality-proven untouched.

## v1.0 results (2026-07-11)
- Build: 7 tasks, all review-gated; champion path EQUAL 50 games at every step; E1 (referee
  hasStalled grace rule) ported and observed live (games end early after deforestation).
- Two plan-level bugs found by the pipeline and fixed: endgame PICK/PLANT livelock
  (Y_PLANT=8500 now outranks DROP/BANK) and the park fallback at 1.0 outranking ALL chop
  throughput values (~0.05-0.67 wood/turn) — the bot trained at t38 then idled 260 turns
  with zero CHOPs; found by command-stream capture vs WAIT; park is now epsilon 0.001.
- V2: legal full games; deterministic (abgate selftest pair delta ≡ 0 ×5); artifacts frozen
  (y1.0.0-yannrepro.min.rs, 94,274 B, MIN-OK). vs WAIT seed 3: 225-23, 122 chops, 54 wood,
  ends t237 via hasStalled.
- **V3 (n=200 pairs vs ringfix3): delta −61.0 [−71.5, −50.5], W/D/L 103/0/297, wood −14.1,
  fruit −4.6 → GATE: REJECT.** Context: head-to-head measures the self-harm axis (calibrated
  same day); −61 sits between ringtune (−27) and trainfruit (−72) — v1.0-faithful is
  materially weaker than the tuned champion in direct play, as expected with unswept G1-G5
  constants, faithful-naive movement, and no mid-game harvesting. NOT a champion candidate
  as-is; ALREADY useful as the gate's diverse sparring opponent (legal, deterministic,
  different strategy family). V4 (boss gate) + V5 (arena) NOT RUN — user directed stop
  before platform interaction; sweeps (G1-G5) + v1.1 (joint move solver) are the obvious
  next levers if pursued.
