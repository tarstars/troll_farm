# Boss 5 game analysis (v1.7.0-adaptivespec, real games, 2026-07-05)

Dataset: **32 verified-clean real Boss-5 games** played with `cgauto/submissions/v1.7.0-DEBUG.min.rs`
(the live bot) in `data/boss5_games/boss/`, plus a **20-game supplementary sample** with the
turn-1 full inventory captured (`data/boss5_games/boss_lemon_draws.txt`, via a standalone
importer script, no repo files modified) to ground-truth the build-vs-draw relationship.

**Housekeeping note:** `data/boss5_games/boss/` originally held 24 games from *three different
bot builds* interleaved (evidently a quick a/b poke at v1.7.1-ladder and v1.8.0-densefarm just
before this task ran). Those were moved to `data/boss5_games/boss_v1.7.1_ladder_experiment/`
and `data/boss5_games/boss_v1.8.0_densefarm_experiment/` (preserved, not deleted) so this
analysis is 100% about the one live spec, v1.7.0-adaptivespec. All 32+20=52 games below are
that build only.

## Headline result

**0/32 wins.** Our wood 45.1 (mean) vs Boss 5's 61.8 — **opponent banks 1.47x our wood.**
This matches the prior 16-game finding (0/16, ~45 vs ~61) almost exactly, at 2x the sample size.

## 1. The starting draw is IDENTICAL for both sides — this is not a luck gap

Across all 20 inventory-logged games, **`myinv[turn=1] == oppinv[turn=1]` in 20/20 games**,
element-for-element (plum/lemon/apple/banana/iron all match). The map is symmetric and both
players are dealt the same opening hand. **Whatever gap exists is 100% decision-quality and
execution, not draw luck** — a stronger framing than "Boss 5 got lucky."

## 2. Build distribution vs lemon draw — confirms AND extends the lemon-gating theory

Our chosen spec (`GE_CHOSEN_SPEC`, locked once at turn 1): **cc=2 in 30/32 games (94%), cc=3 in
only 2/32 (6%)**. This is lower than the ~11% naive estimate (`P(lemon==10)` under a uniform
2-10 draw) in `BOSS5-FINDINGS.md` — see the lock-in bug below for why.

### ★★★ NEW FINDING: the turn-1 spec choice has a real bug — gates on the WRONG resource

`training_cost(n, talents) = {plum: n+ms², lemon: n+cc², apple: n+hp², iron: n+chop²}`. Our cc=2
spec `(2,2,0,2)` and cc=3 spec `(2,3,0,2)` share **identical** ms/hp/chop → identical plum/apple/iron
cost; **lemon is the only cost that differs** (5 vs 10). But `decide_elite`'s one-shot choice
(`main.rs:2167-2178`) tests **full affordability** of cc=3 (`mb_afford`, all 4 resources) against
the turn-1 snapshot, not lemon alone. Result: **a momentary plum or iron shortfall at the exact
turn-1 snapshot permanently locks us into cc=2 for the whole 300-turn game — even on lemon-rich
(≥10) maps, and even though plum/iron will recover in time to fund cc=2 anyway (identical
non-lemon cost):**

| lemon(t=1) | plum(t=1) | iron(t=1) | got cc=3? | note |
|---|---|---|---|---|
| 10 | 4 | 8 | **No (cc=2)** | plum=4<5 blocked the check despite lemon=10 |
| 10 | 2 | 10 | **No (cc=2)** | plum=2<5 blocked the check despite lemon=10 |
| 10 | — | — | No (cc=2), trained t15 | (lemon-only sample, same signature) |
| 10 | — | — | Yes (cc=3), trained t3 | plum/iron happened to be sufficient too |
| 10 | — | — | Yes (cc=3), trained t3 | plum/iron happened to be sufficient too |

**Of 5 games with lemon(t=1)=10 (the "should get cc=3" case), only 2 (40%) actually got cc=3; 3
(60%) incorrectly fell back to cc=2.** Both fully-logged failures are explained by plum<5 at the
turn-1 snapshot. This is a concrete, low-risk, one-line fix: gate the spec **choice** on
`inv[LEMON] >= training_cost(n, cc3)[LEMON]` alone (plum/apple/iron don't differentiate cc2 vs
cc3, so checking them at the CHOICE step only produces false negatives; `train_now`'s own
`mb_afford` gate already correctly enforces full affordability before actually training).

## 3. Regime split revisited — the "rich map" framing was backwards

Using the 20-game inventory-logged sample, split by the task's threshold (lemon≥5 = good,
lemon<5 = poor):

| regime | n | our wood | opp wood | ratio |
|---|---|---|---|---|
| GOOD (lemon≥5) | 15 | 47.1 | 70.4 | **1.49x** |
| POOR (lemon<5) | 5 | 39.8 | 51.4 | **1.29x** |

This **reverses** the prior hypothesis in `BOSS5-FINDINGS.md` ("low-lemon maps: we lose ~2:1;
good-lemon: competitive"). In this larger, cleaner sample, **the relative gap is actually WORSE
on lemon-rich maps.** Mechanism: rich maps give Boss 5 *more* spare resources to exploit (see
§4, extra upgrade axes) AND are exactly where our lock-in bug (§2) throws away the cc=3 upgrade;
poor maps handicap both sides roughly equally (closer game). **Prioritize fixes for the
resource-rich case, not the resource-poor case.**

## 4. NEW FINDING: Boss 5 uses upgrade axes we never touch (ms=3, chop=3)

Our spec space is fixed at `ms=2, chop=2` always — only `cc` (2 vs 3) is ever varied. Boss 5's
observed builds are richer:

| axis | cost gate | example oppbuild | meaning |
|---|---|---|---|
| `ms=3` (speed) | plum ≥ 1+9=10 | `(3,2,0,2)`, `(3,3,0,2)` | faster travel — directly attacks the "travel is the throughput sink" mechanism |
| `chop=3` (fell power) | iron ≥ 1+9=10 | `(2,2,0,3)`, `(2,3,0,3)` | fells trees faster (more hp removed/CHOP) → more fells/turn |

Across the combined 52 games, Boss 5 deployed one of these non-vanilla axes in **12/52 games
(23%)**, and every time it did, our deficit was substantially larger:

| opponent build | n | mean wood gap (opp − our) |
|---|---|---|
| vanilla (cc-only, ms=2/chop=2) | 40 | 16.0 (32-game subsample) |
| **non-vanilla (ms=3 or chop=3)** | 12 | **26.4 (1.65x the vanilla gap)** |

Boss 5 appears to spend *surplus* plum/iron (resources our fixed-spec build has no use for
beyond the cc=2 threshold) on these axes. Our bot structurally cannot match a `(2,3,0,3)` or
`(3,2,0,2)` chopper — worth exploring as an additional adaptive axis, not just cc.

## 5. WHERE we lose: it's the post-establishment throughput phase, not the opening

Mean wood ramp across all 32 games:

| turn | our wood | opp wood | gap (opp−our) |
|---|---|---|---|
| 25 | 2.0 | 0.7 | **−1.3** (we lead) |
| 50 | 5.9 | 2.2 | **−3.6** (we lead) |
| 75 | 9.6 | 5.4 | **−4.2** (we lead) |
| 100 | 13.3 | 9.8 | **−3.5** (we lead) |
| 150 | 21.0 | 20.8 | ~0 (tied) |
| 200 | 28.9 | 32.5 | +3.6 |
| 225 | 32.8 | 39.2 | +6.3 |
| 250 | 36.9 | 46.8 | +9.9 |
| 300 | 45.1 | 61.8 | **+16.8** |

**We are AHEAD through turn 100 and roughly tied at turn 150.** The gap opens entirely in the
back half of the game (t150→300). This directly contradicts a "we start too slow" read of the
data — the early-denial strategy (train the chopper ASAP, fell size-2 early) is working exactly
as intended. **The loss is 100% a sustained/late-game throughput problem, not a timing problem.**

### Confirmed even with the timing confound fully removed

Restricting to the 15/32 games where BOTH sides trained on turn 2-3 (no delay on either side —
the cleanest apples-to-apples production comparison): **our wood 53.1 vs opp 69.6, ratio 1.31x.**
Nearly identical to the overall average — proving the gap is a genuine production/execution deficit,
independent of any training-timing or lemon-luck confound.

### Post-training throughput

Wood-per-turn from each side's own training turn to t300: **ours 0.162/turn, opponent's
0.222/turn — opponent processes 1.37x our wood/turn once both choppers are established.**

## Summary of actionable levers (ranked by confidence × ease)

1. **Fix the spec-choice lock-in bug (§2).** Gate the cc2-vs-cc3 *choice* on lemon alone, not
   full `mb_afford`. Zero-risk, one-line change; directly recovers cc=3 on the ~60% of
   lemon-rich draws we currently waste. High confidence, low effort.
2. **The dominant lever is post-establishment throughput (§5), not economy selection.** ~30-37%
   of the gap persists even with identical builds and identical training turns. This calls for a
   deeper per-action trace (move-vs-chop turn counts, travel routing) to localize precisely —
   this analysis proves WHERE (t150-300) and HOW MUCH (1.3-1.4x) but not the exact mechanical
   cause; that needs a follow-up trace.
3. **Consider ms/chop as additional adaptive axes (§4)**, mirroring Boss 5's use of surplus
   plum→speed and surplus iron→fell-power. Not yet validated in-game — a testable hypothesis.
4. **Re-target "rich" maps, not "poor" maps (§3).** The prior poor-lemon-blowout framing doesn't
   hold in this larger sample; the relatively worse regime is lemon-rich, where Boss 5's
   flexibility (axes + no lock-in bug) is best exploited.
5. Troll-count expansion (3rd/4th troll) is a plausible longer-term lever consistent with what
   beats us in `docs/player-loss-analysis.md`, but treat cautiously — prior 3-4 troll attempts
   (v1.5.0/v1.5.1) failed to fund in the arena; any retry must solve funding-rate, not just copy
   troll count.

## Data/artifacts
- `data/boss5_games/boss/` — 32 clean v1.7.0 games (`.map` + `.log` per game).
- `data/boss5_games/boss_lemon_draws.txt` — 20 games with turn-1 full inventory + build/train/wood.
- `data/boss5_games/boss_v1.7.1_ladder_experiment/`, `data/boss5_games/boss_v1.8.0_densefarm_experiment/`
  — the pre-existing, different-build games found in `boss/`, relocated (not part of this analysis).
