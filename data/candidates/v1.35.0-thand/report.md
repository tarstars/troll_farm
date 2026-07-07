# Candidate v1.35.0-thand — Builder Report

(Persisted by the orchestrator: the builder subagent's Write access to report files was
policy-blocked; content returned in its final message and saved here verbatim in substance.)

**Task:** T-hand — Tempo + funded third hand. Salvage from the parked Scale/Hoard arc (per the
Amendment in docs/superpowers/specs/2026-07-07-last-mile-and-basin-jump-design.md): revive the
dormant GE_MAX_TROLLS feeder slot (2→3) under the live Tempo meta itself, funded by extending the
battle-tested elevated funding stack (iron 65/64, deficit-fruit 63) from Scale-only to ANY pending
ladder hand, including Tempo's. Builder role only; champion-equality gate explicitly waived
(candidate changes Tempo behavior by design). Base tree: 5db7bc9.

## What changed
- TDD tests first, both confirmed FAILING pre-fix:
  - rust/tests/phase_hoard.rs `tempo_ladder_funding_treks_to_deficit_fruit` (Tempo mirror of the
    hoard deficit-trek test; failed with `MOVE 0 3 2` — nearer non-funding banana won).
  - rust/tests/tactics_scale.rs `tempo_wants_third_hand` (3 farm bananas, starter+chopper, t=50;
    failed with want_feeder=false).
- rust/src/botmain.rs: GE_MAX_TROLLS 2→3; VERSION → "1.35.0-thand"; GE_FEEDER_T 60→45
  (ANOMALY, resolved per brief contingency: 60 was dead-constant drift from commit 3e8b2b52 in
  the v1.28.x era, inert while GE_MAX_TROLLS=2 made want_feeder unreachable; 45 = the original
  value, now live and boss/arena-unvalidated on its own — first knob to reconsider if hand
  timing looks off). GE_FEEDER_FARM=3, GE_FEEDER_SPEC=(1,1,1,0) confirmed as assumed.
- rust/src/botmain/planner.rs: `scale_funding = plan.phase != Phase::Tempo && plan.want_feeder`
  → `ladder_funding = plan.want_feeder` (all 3 use sites: iron Mine 65, iron MoveTo 64,
  deficit-fruit 63). Generic wallet band 62 remains Hoard-only (verified: its gate reads
  plan.phase directly). tactics.rs: comment-only updates.
- Diffstat: botmain.rs 6±, planner.rs 29±, tactics.rs 9± (comments), phase_hoard.rs +27,
  tactics_scale.rs +26.

## Gate results
1. cargo build --release: clean (pre-existing warnings only).
2. cargo test --release: 24 suites, 48 tests, 0 FAILED (+2 new tests, green post-fix).
3. Self-determinism: EQUAL 16 games (8 seeds × 2 seats).
4. bundle.py: 68,010 chars → rustc (dot-free copy): exit 0. VERSION/GE_MAX_TROLLS=3/
   GE_FEEDER_T=45/ladder_funding(5 hits) confirmed in bundle.
5. Bundle-inlining sanity: bundled bin vs cargo bot EQUAL 16 games.
6. minify: 68,010 → 41,951 B (58% under cap); rustc on minified copy: exit 0; minified bin vs
   cargo bot EQUAL 16 games.
7. Champion-equality: N/A (waived by design).

## Artifacts
- cgauto/submissions/v1.35.0-thand.rs (69,353 B) and .min.rs (41,951 B); duplicated to
  data/candidates/v1.35.0-thand/ (cmp-identical).
- DEBUG probe for the gatekeeper: data/candidates/v1.35.0-thand/v1.35.0-thand.debug-probe.min.rs
  (41,950 B; DEBUG=true ×1; GE_META=Tempo; rustc exit 0; 2-seed local smoke EQUAL, no crash).

## Next steps (gatekeeper)
collect_debug_games.py <probe> boss 8 + field (incl. denial-style mikdiet 6480914 / plcc
6480966); read @TFFARM: does n reach 3 (t≥45, farm≥3, wallet-dependent), does the hand PLANT,
does wood improve vs the ~50-wood Tempo era norm; ramp.py --last 8 for wood/delta; no crater.
Champion comparison falls on gatekeeper/arena (builder equality was waived).

## Gatekeeper verdict (v1.35.0-thand)

**Probe verified:** `v1.35.0-thand.debug-probe.min.rs` — `const DEBUG: bool = true` (1 hit),
`GE_MAX_TROLLS: i32 = 3` (1 hit). Games collected fresh (no 422s, no throttle wait needed):
boss 8 (gameIds 895391374-895391580), field 6480914×2 (895391677,895391723), field
6480966×2 (895391772,895391814). All @TFFARM lines read `phase=Tempo` confirming the probe.

### 1. THE HAND — n reaches 3?
**0/8 boss games. 0/4 field games. 0/12 overall.** No game ever shows `n=3` in any
`@TFFARM` line; every game ends at `n=2` (chopper only, feeder never trained). First-t of
n=3: N/A (never) in all 12.

Lemon/plum correlation (myinv 1st/2nd numbers = plum/lemon; hand needs 3/3/3 at n=2), read
at the first turn ≥45 with farm≥3 (the earliest plausible `want_feeder` trigger) and by the
peak reached afterward:

| game | trigger t | plum,lemon,apple @trigger | max plum after | max lemon after |
|---|---|---|---|---|
| boss 895391374 | (farm never ≥3 after t45) | – | 2 | 4 |
| boss 895391408 | (farm never ≥3 after t45) | – | 0 | 0 |
| boss 895391443 | (farm never ≥3 after t45) | – | 0 | 4 |
| boss 895391469 | t45 | 0,0,8 | 0 | 2 |
| boss 895391495 | t45 | 3,0,5 | 3 | 0 |
| boss 895391516 | t45 | 0,1,9 | 0 | 2 |
| boss 895391562 | t95 | 1,3,2 | 1 | 3 |
| boss 895391580 | (farm never ≥3 after t45) | – | 0 | 3 |
| fld 6480914-1 | t45 | 4,9,10 | 5 | 9 |
| fld 6480914-2 | t45 | 2,3,8 | 2 | 3 |
| fld 6480966-1 | t45 | 3,0,1 | 3 | 2 |
| fld 6480966-2 | t45 | 0,2,1 | 0 | 2 |

Plum and/or lemon sit below the 3-unit floor for most of the sample (9/12 games never see
BOTH plum≥3 and lemon≥3). But even the one game where all three fruit legs individually
clear 3 at some point (6480914-1: plum peaks 5, lemon peaks 9, apple 10) still never trains
the hand — cross-checking IRON explains why: **in 9/12 games, iron is driven to ~0 by the
chopper's own training cost and never recovers for the rest of the game** (no mining event
after the chopper exists), e.g. 6480914-1 iron 5→0 exactly at the chopper's training turn
(t95) and stays 0 through t300. Code-level cause: `need_iron` (tactics.rs:168-169) is hard-
wired to `want_chopper` only (`have_iron && want_chopper && ...`); once the chopper trains,
`want_chopper` is permanently false, so the Mine/MoveTo-iron candidates (planner.rs:245-259,
gated on `plan.need_iron`) never fire again — even under the elevated `ladder_funding`
bands — although `training_cost` still charges every pending hand `cost[IRON] = n` (2 at
n=2) on any map with iron cells (all 12 sampled maps have iron cells: iron was mined by all
12 before/during chopper training). This is an independent, structural blocker on top of
fruit scarcity, and it alone explains most of the 12/12 misses.

### 2. THE HAND'S WORK — farm at t150+
**N/A — no game ever reached n=3**, so there is no "with-hand" farm sample to compare to the
0-1-hand era norm. For context only, max `farm=` at t≥150 stayed low regardless: boss
0,0,1,0,1,1,1,0 (games in table order above); field 3,1,1,3. The farm is already thin/
collapsed by t150 in nearly every game independent of the hand question.

### 3. ECONOMY (boss, `ramp.py --last 8`)
```
t75 : us 10.0  opp  3.5  delta +6.5
t150: us 23.0  opp 15.9  delta +7.1
t225: us 34.8  opp 33.0  delta +1.8
t300: us 45.4  opp 51.1  delta -5.8
wins 2/8 (25%)   avg final wood 45.4   late(225->300) us +10.6 vs opp +18.1
```
Per game (final wood us-opp): 40-57(L), 35-46(L), 48-57(L), 42-42(L), 56-65(L), 44-46(L),
52-51(W), 46-45(W). Min final wood = 35 (>25 floor: OK). t300 delta -5.8 (better than the
-12 floor: OK). avg final wood 45.4 clears the ≥45 gate but sits well under the Tempo-era
~50 norm. No crash / no panic in any of the 12 raw logs (grepped clean); all `scores`
entries are normal positive pairs (no -2 DNF sentinel). **Readout 3 HOLDS.**

### 4. FUNDING TAX — wood at t75 (boss, era norm ~10-14)
Per game: 12, 10, 16, 10, 14, 10, 0, 8 → **avg 10.0** (sits at the floor of the era norm,
pulled down by one 0-wood outlier, game 895391562, where the chopper itself didn't train
until t87). Field t75 (supplementary, opponent-dependent, not gate-relevant): 0, 20, 30, 14.
No evidence of a broad early-game funding tax beyond ordinary variance — the one low outlier
is a slow-chopper-draw map, not a hand-funding errand (the hand isn't even eligible until
nchop≥1).

### 5. FLAPS (final value per game, boss)
6, 4, 5, 7, 12, 7, 9, 1 → **8/8 ≤15** (bar was ≥6/8). Holds comfortably.

### 6. FIELD (score margins, us-opp, from `scores`)
- 6480914 g1 (895391677): LOSS 207-260 → **-53**
- 6480914 g2 (895391723): WIN 241-186 → **+55**
- 6480966 g1 (895391772): WIN 394-360 → **+34**
- 6480966 g2 (895391814): WIN 302-241 → **+61**

Record 3W-1L, worst margin -53 (floor is -150). **Readout 6 HOLDS.**

### Verdict: **FAIL — inert**
Readouts 3 and 6 both hold on their own terms, but readout 1 shows the hand trains in **0/8**
boss games (need ≥3/8), and the brief's explicit override applies: *"if the hand NEVER
trains, the candidate is inert = FAIL with note 'inert'."* v1.35.0-thand is behaviorally
indistinguishable from the pre-existing 2-troll Tempo baseline in all 12 games sampled — the
GE_MAX_TROLLS 2→3 change never engages.

**Most actionable observation:** the dominant, structural blocker (not just map-dependent
fruit scarcity) is that `need_iron` (tactics.rs:168) is gated on `want_chopper` alone, so the
bot stops mining iron the moment the chopper trains — permanently starving any later pending
hand of the flat `n`-iron cost every spec carries, on every map that has iron (12/12 here).
Before re-testing this candidate, extend `need_iron` (or add a parallel condition) to also
cover `want_feeder`, so the elevated `ladder_funding` Mine/MoveTo-iron bands (65/64) can
actually fire once the chopper already exists.
