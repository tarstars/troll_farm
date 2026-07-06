# Player loss analysis (v1.7.0-adaptivespec vs real Gold players, 2026-07-05)

Dataset: real games via `TestSession/play` with `cgauto/submissions/v1.7.0-DEBUG.min.rs`
(the live bot) against two frozen elite-Gold snapshots:
- **runninglvlan** (agentId 6481102): 12 games, **4W/8L (33% win)**. `data/boss5_games/6481102/`
- **nmahoude** (agentId 6480842): 10 games, **2W/8L (20% win)**. `data/boss5_games/6480842/`

Both opponents run a **bigger economy than our fixed 2-troll build** (`GE_MAX_TROLLS=2` hard
caps us at starter + 1 chopper, always). This single structural fact — not denial, not wasted
travel, not map layout — is the dominant driver of the losses below.

## runninglvlan: always a 3-troll economy

Every single game (win or loss), runninglvlan's final build is the same 3-troll composition:
`starter(1,1,1,1) + harvester(2,2,2,0) + chopper(2,3,0,2)`. The middle troll is a **pure
harvester with chop=0** — it never fells, only harvests/plants, feeding the economy so the cc=3
chopper can be funded and kept supplied. We never exceed 2 trolls.

### What separates the 4 wins from the 8 losses: THEIR training speed, not ours

| | our train turn (myT) | opp chopper train turn (oppT) |
|---|---|---|
| **WINS** (n=4) | 3, 7, 9, 15 (mean 8.5) | 39, 47, 27, 53 (**mean 41.5**) |
| **LOSSES** (n=8) | 3, 11, 79, 3, 3, 15, 67, 5 (mean 23.3) | 37,13,67,2,2,2,43,9 (**mean 21.9**, median 11) |

Our own training timing is similar in both buckets (mostly fast, with 1-2 unlucky-draw
outliers). The real split is **the opponent's chopper**: when it trains late (their own economy
stumbles, mean t41.5), we win; when it trains early (mean t21.9, half of the 8 losses at t≤9), they win. **We
only win when the opponent's draw is unlucky — we are not ahead on an even footing.** This is
the same identical-symmetric-draw dynamic documented in `docs/boss5-game-analysis.md` (§1).

### Loss wood ramp — same signature as Boss 5: we lead early, they take over late

| turn | our wood | opp wood | gap |
|---|---|---|---|
| 25 | 3.0 | 0.0 | −3.0 (we lead) |
| 50 | 8.6 | 0.0 | −8.6 (we lead) |
| 75 | 13.4 | 0.8 | −12.6 (we lead) |
| 100 | 17.5 | 4.5 | −13.0 (we lead) |
| 150 | 26.1 | 21.0 | −5.1 (still ahead) |
| 200 | 34.4 | 38.8 | +4.4 (overtaken) |
| 250 | 42.0 | 52.8 | +10.8 |
| 300 | 49.1 | 67.8 | **+18.6** |

We lead comfortably through turn 100-150 — the extra 3rd troll (harvester) doesn't show up as
an advantage until the midgame, then it compounds: more hands means more fruit funneled to the
chopper and more seed/farm upkeep, so their throughput overtakes ours between t150-200 and the
gap grows for the rest of the game.

## nmahoude: always a 4-troll "accumulate" economy — our worst matchup

Every game, nmahoude's final build is `starter(1,1,1,1) + 2×harvest/chop-hybrid(2,2,1,1) +
ONE premium chopper (2,4,0,3)` — cc=4 (double our carry capacity) AND chop=3 (faster felling),
funded by two extra all-purpose trolls. This matches the "Legend-tier" 4-troll archetype
already decoded from `Tchoubidouwa123` in `docs/BOSS5-FINDINGS.md`.

### Loss wood ramp — the most extreme accumulate signature in the whole study

| turn | our wood | opp wood | gap |
|---|---|---|---|
| 25 | 1.5 | 0.0 | −1.5 |
| 50 | 5.5 | 0.0 | −5.5 |
| 75 | 12.8 | 0.1 | −12.6 |
| 100 | 21.8 | 0.2 | **−21.5** (we lead massively) |
| 150 | 36.2 | 0.8 | **−35.5** (we lead massively) |
| 200 | 49.2 | 33.1 | −16.1 (still ahead) |
| 250 | 60.8 | 71.5 | +10.8 (overtaken) |
| 300 | 72.1 | 100.6 | **+28.5** (worst gap of any dataset) |

Through turn 150, the opponent has banked essentially **zero** wood (mean 0.8) while we're
already at 36.2 — a **35-wood lead we're throwing away.** Then, in the 150 turns from t150→300,
the opponent's mature farm gets mass-harvested by the cc=4/chop=3 unit:

- opponent: (100.6 − 0.8) / 150 = **0.665 wood/turn** during the harvest burst
- us: (72.1 − 36.2) / 150 = **0.239 wood/turn** in the same window
- **ratio: 2.78x** — nearly 3x their post-maturity throughput vs ours, the largest throughput
  gap found anywhere in this study (bigger than the ~1.3-1.4x found vs Boss 5).

`trees_end` (remaining trees at t300) across the 8 losses ranges 1-9, but the two MOST lopsided
games (wood gap 52 and 45, the worst in the whole study) are also the two most heavily
deforested (trees_end 2 and 1) — the map gets nearly clear-cut in the worst blowouts, with the
bigger 4-troll economy capturing the lion's share once its cc=4/chop=3 unit comes online. This
isn't a clean monotonic rule across all 8 losses (some higher-gap games still have trees_end=9),
but the extreme cases line up.

### The 2 wins

- `895230549`: opp's premium chopper trained late (t35 vs our t11) — final wood tied 96-96 (win
  by the composite tiebreak). Same "opponent's economy stumbled" pattern as runninglvlan.
  Notably this is the ONE nmahoude game where OUR wood also reached triple digits — we can match
  scale when given the extra ~25 turns of head start.
- `895230571`: BOTH trained immediately at t3 — and we won outright, 108-101, despite facing the
  full 4-troll economy. This is the single cleanest evidence that **speed/symmetry can
  occasionally beat scale**, but it is the exception (1/10), not the rule.

## Map-feature check: no meaningful correlation

Correlated final wood-gap against map walkable-cell-count (a proxy for map size/openness) per
opponent:

| opponent | corr(walkable cells, wood gap) |
|---|---|
| boss | 0.04 |
| runninglvlan | 0.25 (weak) |
| nmahoude | −0.22 (weak) |

None of these are meaningfully strong. **The losses are driven by build/economy-scale mismatches,
not map geometry** (size, water fraction, iron-cell count all showed no clear pattern either).

## Cross-opponent pattern (the single biggest finding of this report)

The SAME signature appears against Boss 5, runninglvlan, AND nmahoude: **we lead or are tied
through roughly turn 100-150, then get decisively overtaken in turns 150-300** as the opponent's
larger/more mature economy converts stored potential (extra trolls, matured farms, premium
choppers) into wood faster than our fixed 2-troll build can sustain. This is not a denial
problem, not a training-timing problem (our early game is fine or better), and not a map-layout
problem — it is a **throughput/scale ceiling** that gets exposed exactly when games run long.

## Actionable levers

1. **The core structural handicap is our hard 2-troll cap (`GE_MAX_TROLLS=2`).** Both real Gold
   opponents we lose to run 3-4 trolls, specifically using the extra troll(s) as harvesters/
   funders that let their chopper reach a bigger spec (cc=3, or cc=4+chop=3) and stay fed. This
   matches `docs/boss5-game-analysis.md`'s conclusion that the deficit is throughput, not timing.
2. **Any 3rd/4th-troll retry must solve funding RATE, not just copy troll count** — memory
   records prior attempts (v1.5.0-harvest4, v1.5.1-cc4legend) failed in the arena (rank 491, the
   cc=4 unit never finished funding). The new data here narrows the target: the extra troll(s)
   only need to pay off by ~t150 (that's where the current 2-troll build starts losing the race)
   — a later-training 3rd troll that completes the funding by t150 should flip exactly the games
   this report shows us losing.
3. **We are NOT behind at the open — do not touch the early game.** Every loss bucket in this
   report shows us leading or tied through t100-150. Whatever change is made, preserve the
   turn-1 early-chopper denial behavior; the fix belongs entirely in the t150+ phase.
4. **Do not raid/counter-deny nmahoude's accumulate farm** — memory (`denial-vs-production-
   frontier.md`) already found delaying/accumulating ourselves LOSES (v1.6.0, 0/6 vs
   runninglvlan) and raiding previously regressed. The lever is scaling OUR OWN throughput to
   match the t150-300 explosion, not suppressing theirs.
5. This dataset and `docs/boss5-game-analysis.md` are mutually reinforcing: fixing the
   spec-choice lock-in bug and/or adding ms/chop as adaptive axes (found there) would likely help
   here too, since both player opponents also fund richer specs (cc=3, cc=4+chop=3) than our
   fixed cc=2/ms=2/chop=2.

## Data/artifacts
- `data/boss5_games/6481102/` — 12 games vs runninglvlan (`.map` + `.log` per game).
- `data/boss5_games/6480842/` — 10 games vs nmahoude (`.map` + `.log` per game).
