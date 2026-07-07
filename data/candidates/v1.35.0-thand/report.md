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

## Fix T-hand.1

**Task:** fix the two structural blockers the gatekeeper verdict identified (above) and
re-freeze v1.35.0-thand IN PLACE (iteration 2). Base tree: this branch, on top of e8ed378
(the FAIL gate commit).

### What changed
- TDD, `rust/tests/tactics_scale.rs`, confirmed FAILING pre-fix:
  - `tempo_wants_third_hand` state changed from three farm bananas (farm_now=3) to ONE
    (farm_now=1) — failed with `want_feeder=false` (pins fix b, the farm≥3 gate).
  - New `tempo_wants_third_hand_farm3`: the original 3-banana body kept verbatim as a
    non-regression companion (farm_now=3 must still want the hand once the gate drops to 1).
  - New `tempo_hand_iron_funding_after_chopper`: reuses the farm3 construction, adds an iron
    cell + inventory `[5,5,5,0,0,0]` (every fruit leg clears the feeder spec's cost, iron
    alone sits at 0 < cost[IRON]=2) — failed with `need_iron=false` (pins fix a, the
    want_chopper-only gate).
  - Both confirmed FAILING against the pre-fix tree; the untouched `tempo_wants_third_hand_farm3`
    passed immediately (sanity that the harness/base construction was right).
- `rust/src/botmain/tactics.rs` (TEMPO branch only — Scale's own `need_iron` from e09ac48 is
  untouched, it's a separate branch of the same `if meta == Meta::Scale` split): `need_iron`
  widened from `have_iron && want_chopper && ...` to
  `have_iron && (want_chopper || want_feeder) && ...` — iron mining now stays wanted while
  ANY pending hand (chopper or feeder) is unfunded, not just the chopper. `cost` already
  switches to `GE_FEEDER_SPEC` whenever `!want_chopper`, so `cost[IRON]` correctly reflects
  the feeder's own (small, n-only) iron price once the chopper already exists.
- `rust/src/botmain.rs`: `GE_FEEDER_FARM` 3 -> 1 with an inline comment — the hand IS the
  farm's planter, so gating it on an already-healthy farm blocked the cure (gatekeeper
  v1.35.0 verdict: farm sits at 0-1 after t45 in half the boss games sampled, so `farm_now>=3`
  was rarely satisfied in exactly the situation the hand exists to fix).
- Diffstat: tactics.rs 8± (logic + comment), botmain.rs 1± (comment), tactics_scale.rs +47/-13.

### Gate results
1. `cargo test --release`: all suites green — 6/6 in `tactics_scale.rs` (the two new/modified
   tests now pass; `tempo_wants_third_hand_farm3` and every other suite, incl. Scale/Hoard/
   Factory phase tests and `phase_hoard.rs`'s `tempo_ladder_funding_treks_to_deficit_fruit`,
   unaffected — Scale's `want_hand` path does not read `GE_FEEDER_FARM` at all (it has its own
   `SCALE_MIN_TURN` gate), confirmed by reading tactics.rs's Scale branch: no reference).
2. Self-determinism: `equality target/release/bot target/release/bot 8 300 target/release/bot`
   -> `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
3. Champion-equality: N/A (waived by design, per the original T-hand brief — Tempo behavior
   changes intentionally).
4. `tools/bundle.py`: `src/botmain.rs -> target/refactor/bundled.rs: 68619 chars`. Grep
   confirms in the bundle: `VERSION = "1.35.0-thand"`, `GE_MAX_TROLLS: i32 = 3`,
   `GE_FEEDER_FARM: usize = 1` (T-hand.1 comment present), `ladder_funding = plan.want_feeder`,
   and the widened `need_iron = have_iron && (want_chopper || want_feeder) && ...` line.
5. rustc compile-check on the full bundled source (dot-free copy): exit 0 (`SRC-COMPILE-OK`).
6. Bundle-inlining sanity: bundled bin vs `target/release/bot` ->
   `EQUAL: 16 games (8 seeds x 2 seats), all command streams identical`.
7. `tools/minify.py`: `68619 -> 41992 chars (61%)` (58% under the 100,000 B cap).
8. rustc compile-check on the minified copy (dot-free copy): exit 0 (`MIN-COMPILE-OK`).
9. Minified bin vs `target/release/bot`: `EQUAL: 16 games (8 seeds x 2 seats), all command
   streams identical`.
10. DEBUG probe rebuilt: `sed` flip confirmed (`const DEBUG: bool = true;` x1 in the pre-minify
    source), minified to 41,991 B, rustc compile-check exit 0, 2-seed local smoke ->
    `EQUAL: 4 games (2 seeds x 2 seats), all command streams identical` (no crash; DEBUG only
    echoes to stderr, so stdout-parity holds as documented).

### New sizes
- `cgauto/submissions/v1.35.0-thand.rs`: 69,353 B -> **69,968 B**.
- `cgauto/submissions/v1.35.0-thand.min.rs`: 41,951 B -> **41,992 B** (58% under cap).
- `data/candidates/v1.35.0-thand/v1.35.0-thand.rs` / `.min.rs`: byte-identical (`cmp`-verified)
  to the `cgauto/submissions/` copies above.
- `data/candidates/v1.35.0-thand/v1.35.0-thand.debug-probe.min.rs`: 41,950 B -> **41,991 B**.

### Next steps (gatekeeper, re-run)
Same recipe as before: `collect_debug_games.py <probe> boss 8` + field (incl. mikdiet
6480914 / plcc 6480966); read `@TFFARM`: does `n` now reach 3 even on thin-farm maps (farm_now
was the old blocker) and does iron stay funded past the chopper's training turn (was the other
blocker); `ramp.py --last 8` for wood/delta; no crater. If the hand still doesn't train, check
whether iron income itself (not just the gate) is the residual bottleneck — no mining event
existed before this fix on 9/12 sampled maps, so the *rate* of iron income once mining resumes
is untested.

## Gatekeeper verdict #2 (v1.35.0-thand, post T-hand.1)

**Probe verified:** `v1.35.0-thand.debug-probe.min.rs` — `const DEBUG: bool = true` (1 hit),
`GE_MAX_TROLLS: i32 = 3` (1 hit), `GE_FEEDER_FARM: usize = 1` (1 hit), `ladder_funding =
plan.want_feeder` (4 hits: definition + 3 use sites 65/64/63), widened
`need_iron = have_iron && (want_chopper || want_feeder) && inv[IRON] < cost[IRON] &&
afford_fruit_only(inv, &cost)` (confirmed by line-offset read of the minified file). Cross-read
against the live source tree (`rust/src/botmain/tactics.rs`, `state.rs`) confirms the probe
matches HEAD (`git diff b041c25 -- .../v1.35.0-thand.debug-probe.min.rs` = empty).

**Boss games — reused, not re-collected.** On starting this verdict, `data/boss5_games/boss/`
already held 8 fresh games (`895394529/576/602/649` at 17:04-17:05, `895413055/073/097/149` at
18:44), all timestamped AFTER the b041c25 fix commit (17:02) — evidently an earlier, interrupted
pass at this same verdict (a byte-identical scratchpad copy of the probe, `probe_check.rs`/
`probe_check_bin`, sits at 17:03, `cmp`-clean against the committed probe). Rather than burn
more of the (already ~3/4-consumed) daily play budget re-collecting an equivalent sample, I
verified these 8 are genuine fixed-probe output by tracing observed behavior against the live
`tactics.rs` logic turn-by-turn (see readout 1) — every non-training outcome is fully explained
by legitimate gate/affordability states under the CURRENT code, with no contradiction found (had
the old probe been used, `farm_now>=1` cases with fruit already ready would have trained; none
exist in-sample where old-vs-new would visibly diverge, but several exist where the NEW gate is
the only thing tested and it's cleanly consistent). Field games were collected fresh this pass
(no reuse possible — none existed post-fix): 6480914×2, 6480966×2, no HTTP 422s encountered.

Boss gameIds: 895394529, 895394576, 895394602, 895394649, 895413055, 895413073, 895413097, 895413149.
Field: 6480914×2 (895415974, 895415996), 6480966×2 (895416024, 895416046).

### 1. THE HAND — n reaches 3?
**0/8 boss games. 0/4 field games. 0/12 overall.** `maxn=2` in every single game (grepped
`n=` across all `@TFFARM` lines); first-t of n=3: N/A (never) in all 12. "Iron resumes mining
after the chopper" is N/A for the same reason as verdict #1 (no game ever gets far enough to
check) — but this time the reason is upstream of `need_iron` entirely.

**New root cause: `farm_now` collapses to literal ZERO for most of the game — not merely thin —
so even the relaxed `GE_FEEDER_FARM=1` gate fails.** Per-game count of `@TFFARM` samples with
`farm=0` for t≥45 (out of ~52 five-turn samples per game): 46, 45, 37, 40, 33, 38, 34, **52**
(i.e., 63%-100% of sampled turns). Final `farm=` at t=300 is **0 in all 8/8 games**.

| game | trigger t (farm≥1) | plum,lemon,apple @trigger | iron @trigger | max plum after | max lemon after | max apple after |
|---|---|---|---|---|---|---|
| 895394529 | 45 | 0,2,8 | 2 | 1 | 2 | 15 |
| 895394576 | 45 | 4,0,6 | 4 | 4 | 2 | 15 |
| 895394602 | 45 | 0,4,1 | 2 | 2 | 4 | 3 |
| 895394649 | 45 | 0,0,6 | 2 | 0 | 0 | 8 |
| 895413055 | 45 | 5,5,8 | 4 | 5 | 5 | 11 |
| 895413073 | 45 | 1,3,2 | 4 | 1 | 3 | 3 |
| 895413097 | 60 | 0,0,2 | 1 | 0 | 1 | 3 |
| **895413149** | **never** | – | – | 4 | 3 | 21 |

Three distinct failure patterns, all tracing back to the same collapsed farm:
1. **Farm never reaches even 1** (895413149, cleanest case): plum/lemon/apple/iron all clear the
   feeder's cost (3/3/3/2) and STAY cleared continuously from t45 to t300 (255 straight turns:
   p=4,l=3,a=7→21,i=4 the whole way) — every precondition except `farm_now>=1` holds for nearly
   the whole game, yet `@TFFARM` never once logs `farm>=1` after t15, so `want_feeder` is never
   even eligible. This is a pure gate failure, not a resource failure.
2. **Late-chopper resource depletion + lemon non-recovery** (895413055, 895413097): fruit+iron
   are all sufficient at t45 while the chopper hasn't trained yet (nchop=0 blocks `want_feeder`
   regardless of farm), but the chopper itself trains late (t55, t59) and its own training cost
   drains the same pool (e.g. 895413055: p,l,i go 5,5,4 → 0,0,0 exactly at the training turn);
   lemon in particular never recovers above 0-1 for the remaining ~240 turns, so
   `afford_fruit_only` stays false even though `want_feeder`'s gate itself would now pass.
3. **Single-fruit-type ceiling** (895394529/576/602/649/073): plum or lemon (varies by map) caps
   at 0-2 for the entire game and never simultaneously clears 3 alongside the other two legs.

### 2. THE HAND'S WORK — farm at t150+
**N/A — no game ever reached n=3.** For context, max `farm=` at t≥150 stayed at/near collapse
regardless: boss 1, 0, 1, 1, 1, 1, 1, 0 (game order as above) — indistinguishable from verdict
#1's context numbers (0,0,1,0,1,1,1,0); the farm is already dead by t150 independent of the hand.

### 3. ECONOMY (boss, `ramp.py --last 8`)
```
t75 : us  10.2  opp   2.6  delta  +7.6
t150: us  21.5  opp  14.6  delta  +6.9
t225: us  31.5  opp  32.2  delta  -0.8
t300: us  40.6  opp  52.9  delta -12.2
wins 0/8 (0%)   avg final wood 40.6   late(225->300) us +9.1 vs opp +20.6
```
Per game (final wood us-opp): 38-56(L), 40-54(L), 42-48(L), 48-60(L), 42-49(L), 50-62(L),
30-38(L), 35-56(L). Min final wood = 30 (>25 floor: OK, but below verdict #1's min of 35).
No crash/panic in any of the 8 raw logs (grepped clean); all `scores` entries are normal
positive pairs. **Compare vs verdict #1 (45.4 avg, −5.8 delta, min 35, wins 2/8): avg final
wood 40.6 < 45 (gate MISS) and t300 delta −12.2 is worse than the −12 floor (gate MISS, albeit
marginal) — this is a regression on both economy sub-gates, not the improvement the hand was
meant to deliver. Win rate also dropped 25%→0%, though n=8 is too small to weight that alone.**
**Readout 3 FAILS.**

### 4. FUNDING TAX — wood at t75 (boss, era norm 10-14)
Per game: 12, 12, 12, 10, 6, 18, 2, 10 → **avg 10.25** (matches verdict #1's 10.0; sits at the
floor of the era norm). One low outlier (2, game 895413097) traces to a late chopper draw
(trains t59), the same pattern as verdict #1's single low outlier — not hand-funding-related,
since the hand is never even eligible this early. No evidence of a new broad funding tax.

### 5. FLAPS (final value per game, boss)
7, 6, 11, 14, 7, 15, 8, 5 → **8/8 ≤15** (bar was ≥6/8). Holds comfortably, same as verdict #1.

### 6. FIELD (score margins, us-opp, from `scores`)
- 6480914 g1 (895415974): LOSS 401-540 → **-139**
- 6480914 g2 (895415996): LOSS 234-387 → **-153** ← worse than the −150 floor
- 6480966 g1 (895416024): WIN 204-161 → **+43**
- 6480966 g2 (895416046): LOSS 282-392 → **-110** (game concluded early at t269, no crash,
  normal score pair — not counted as a DNF)

Record 1W-3L (verdict #1 was 3W-1L on the same two opponents; only 2 games/opponent each pass,
so this reversal is largely sample noise, not a reliable trend on its own). Worst margin **-153**
breaches the −150 floor. **Readout 6 FAILS.**

### Verdict: **FAIL — still inert, plus new economy/field regressions**
Per the brief, PASS requires the hand to train in ≥3/8 AND readout 3 holds AND readout 6 holds.
All three miss:
- Readout 1: hand trains in **0/8** (need ≥3/8).
- Readout 3: avg final wood **40.6 < 45**; t300 delta **-12.2** worse than the −12 floor.
- Readout 6: worst field margin **-153** worse than the −150 floor.

T-hand.1 correctly fixed the two blockers it targeted (need_iron scope, farm gate 3→1 — no
evidence either one is still active as a blocker: no game in this sample straddles the "iron
funded, want_feeder eligible" boundary the OLD code would have failed but the NEW code passes,
because a THIRD, more fundamental blocker sits upstream of both).

**Most actionable observation:** `GE_FEEDER_FARM=1` is still a nonzero floor, and `farm_now` is
routinely **exactly 0** (not merely "thin") — 63-100% of sampled turns per game, and 8/8 games
end with `farm=0`. Game 895413149 isolates this cleanly: fruit (p=4,l=3,a=7→21) and iron (i=4)
clear the feeder's full cost continuously for 255 straight turns (t45-t300), yet `want_feeder`
never once becomes eligible because `farm_now` never reaches even 1. The hand exists specifically
to rescue a collapsed farm, so gating it on `farm_now>=1` is the same catch-22 `>=3` was, one
notch smaller. Next fix to try: `GE_FEEDER_FARM` 1→0 (drop the farm-density precondition
entirely — `nchop>=1 && n<GE_MAX_TROLLS && turn>=GE_FEEDER_T` is already a sufficient gate; the
farm term was never load-bearing in the direction that matters, since a HEALTHY farm was the
original v1.34-era reason for the gate, not a floor a DEAD farm needs to clear). Separately,
watch the late-chopper-train games (895413055/097): even at farm-gate=0, `afford_fruit_only`
would still block them because lemon craters to 0-1 for ~240 turns after the chopper's own
training cost drains the pool — that may need its own fix (e.g. reserve lemon from the chopper's
cost, or fund the feeder before the chopper on lemon-tight draws) if farm-gate=0 doesn't clear
the whole sample.
