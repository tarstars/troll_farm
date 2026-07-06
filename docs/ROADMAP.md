# ROADMAP — Gold rank ~117 → sub-100 (the Legend bar)

**Written 2026-07-06 for the executing agent.** This is a *recipe book*, not a discussion:
follow the steps exactly, in order, one experiment at a time. When an outcome contradicts the
expectation written here, do NOT improvise a new theory — revert to the frozen best (§3.G),
record what happened (§8), and move to the next queued experiment. Everything here was
verified against the real project state on 2026-07-06.

Companion docs: `cgauto/HANDOFF.md` (background; PARTIALLY STALE — its "current state" §1 is
from the v1.4.5 era), `docs/BOSS5-FINDINGS.md` (Boss-5 mechanics + how to play the real boss),
`docs/motion-findings.md` (motion solver, done), `docs/silver-experiment-log.md` (append-only
experiment history).

---
## 0. STATE — update this table after EVERY arena verdict

| Item | Value (2026-07-06 11:10) |
|---|---|
| Live arena submission | **v1.20.0-motion (re-submitted 14:50)** after v1.24.0-fruitbank converged at **124 @ 17.5 = −1.0 → REVERTED** (starter chased 1-pt fruit instead of chop-helping 4-pt fells). |
| Arena baseline / fallback | **v1.20.0-motion 118 @ 18.6** (noise band ±0.2). Working tree RESTORED to this exact source (14:55). |
| ★ DAY VERDICT 2026-07-06 | 4 arena experiments, all reverted (motion −0.3/−0.5, sched dead, seedloop −2.8, fruitbank −1.0). **The decide_elite knob well is DRY — every bolt-on loses.** The road to +1.3 = Phase R (L2 jobs layer, coordinated policy). R1/R2 STARTING. |
| Seedloop post-mortem | v1.23.0 cratered (205 @ 15.6): ripening mid-map bananas = 3-4-wood gifts for field cc3 choppers (A/B vs RunninglVlan: opp wood 46→67). Family frozen; §5 dead ends. |
| ⚠ NEW IRON RULE (2026-07-06) | The boss gate alone is NOT sufficient for economy changes: add a **field gate** (games vs rank-100-140 players via collect_debug_games with their agentIds) before any arena submit. The arena field ≠ Boss 5. |
| T1 (decide_sched) | **CLOSED-FAILED 2026-07-06** (1/12, wood 13 — see §4/§5) |
| T2.a (late feeder) | **EXECUTED 2026-07-06, INCONCLUSIVE**: never trains — dead farm (<5) + empty wallet; reopen after T2.0b (wallet refills from fruitbank) |
| ★ T2.0 v1.23.0-seedloop | **GATE PASSED + SUBMITTED 12:04** — root cause was: anti-starvation fallbacks EAT the seed reserve; seeds 0 all game, farm dead by t140. Fixed (reserve widened to our-half + fallbacks spare it): farm alive t150+ in 10/12 games. |
| ★ T2.0b v1.23.1-fruitbank | Boss gate was good (3/15, wood 51.3, delta −6.2; wins the fruit-decided games) but **submission CANCELLED** — it contains seedloop, which cratered vs the field. Both frozen; re-decide after the FIELD analysis (T3) explains the crater. |
| Frozen best (converged) | **v1.20.0-motion — rank 117/531, score 18.4** |
| Fallbacks (frozen, in `cgauto/submissions/`) | v1.19.0-densetight (118 @ 18.2), v1.13.0-tightfarm (~120 @ 17.9) |
| Goal | arena-room rank ≤ 99 (user goal); boss bar = score ~26.2 @ rank 98; Legend = top 97 |
| Primary loss metric | wood delta us−boss at t300 = **−15.3** (115-game baseline; see §1) |
| Motion (done, banked) | real-engine BLOCK rate 4.1% → **1.73%** (v1.21.0); do not gold-plate further |
| `api_submit.py` default | v1.21.0-motion.min.rs (**keep = frozen best**, an hourly cron at :13 may resubmit the default) |
| Bot source of truth | `rust/src/main.rs`, `fn decide_elite` (VERSION "1.21.0-motion", DEBUG=false) |

## 1. The goal and the honest math

- Scoreboard: `cg_rank.py` line `ARENA-ROOM: tass rank R/531 Gold score S`. **Only this line
  counts.** (The second line, from the codingame package, is a WRONG scope — ignore its rank.)
- **GOAL MATH (corrected 2026-07-06 via `field_targets.py` — the earlier "+7.5" figure was
  wrong):** there are TWO separate bars. (1) **User goal, rank ≤99 in the Gold room = score
  ≈ 19.7-19.9** (measured: ranks 95-113 hold 19.0-19.9) → from baseline 18.4 that is
  **+1.3-1.5 points — about 2-3 field-validated knob wins** (v1.13→v1.20 banked +0.5).
  (2) **Legend promotion = beat Boss 5 @ ~26.2** — much farther; ignore until (1) is done.
- Corollary: the opponents that matter for the goal are the **19-20-score FIELD players**
  (Tchoubidouwa123 @98, RunninglVlan @102, nmahoude @110 …, roster via
  `uv run --no-sync python cgauto/field_targets.py 95 130`), NOT the boss. The field gate
  is the primary judge for every change; the boss gate remains a useful economy probe only.
- WHERE we lose (quantified over 115 real Boss-5 games, all with IDENTICAL 2-troll builds
  `1.1.1.1` + `2.2.0.2` on both sides): wood delta us−boss = **+4.1 @t75, +2.8 @t150,
  −3.1 @t225, −15.3 @t300**. We WIN the opening; the boss out-produces us ~2× in the last
  quarter (late gain: us +10..16, boss +20..30). Cause: our single starter cannot keep the
  tight radius-2 farm refilled, so the chopper runs out of near-bank fell-ready trees and
  roams/idles. **The lever = sustained LATE farm supply.** (Memory: `late-throughput-ceiling`.)
- Expect most experiments to FAIL. That is normal here; the deliverable of an experiment is
  a *recorded verdict*, and the arena must always end the day on the frozen best.

## 2. Non-negotiable rules

1. **One change per experiment.** Preassigned version number (§4), bump `const VERSION` in
   `main.rs` before freezing. Never stack untested changes.
2. **The sim (bench/winrate) MUST NOT judge economy changes.** It rewards the wrong things
   (transfer wall; v1.0.4 was 90.5% sim / 33% real). Sim is only for: compiling, unit tests
   (`cargo test`), and motion micro-verification. Economy gates = real Boss-5 games (filter,
   §3.D) + the arena (judge, §3.F).
3. **Never submit a DEBUG build to the arena.** Arena code always has `const DEBUG: bool = false;`.
4. **Freeze before submit** (§3.B): `cgauto/submissions/vX.Y.Z-name.rs` + `.min.rs`, and the
   `.min.rs` must pass the compile-check. Never overwrite or delete existing frozen versions.
5. **Verify submissions only by the arena** (§3.F): the ARENA-ROOM rank/score/agentId change.
   Never trust script exit codes, and never trust `const VERSION` labels in old artifacts.
6. **Accept/revert by score** (§3.G). If a submission converges below baseline − 0.3, resubmit
   the frozen best immediately. If two consecutive experiments regress, stop and write a
   findings summary for the user instead of trying a third.
7. **Play-API throttle discipline:** ≤ 12 boss games per burst. On HTTP 422 or empty games:
   stop, wait ≥ 15 minutes, halve the burst. (Hard throttling recovers over tens of minutes.)
8. **cwd discipline:** run `cgauto/*.py` from `/home/tarstars/prj/troll_farm`; run cargo from
   `/home/tarstars/prj/troll_farm/rust`. All python via `uv run --no-sync python`.
9. **Keep `api_submit.py`'s default file = the frozen best** (edit its line ~12 when the best
   changes). An hourly cron (id 0b369c72, at :13) advances this goal and may resubmit the
   default; a stale default would silently clobber a newer live bot.
10. **Do not touch** `rust/src/game/engine.rs` (validated referee model), the frozen
    submissions, or the motion post-passes in `decide_elite` (watchdog + proactive re-route —
    they are measured-good).
11. Commit/push only when the user asks. Keep `docs/silver-experiment-log.md` appended (§8).
12. Do not start Tier-4 items (§4) without the user.

## 3. The standard experiment loop (the ONLY workflow)

Every experiment = A→H. Copy-paste the commands; expected outputs are noted.

**A. Edit + build + unit test**
```
cd /home/tarstars/prj/troll_farm/rust
# make the ONE queued change in src/main.rs; bump const VERSION (line ~10)
cargo build --release        # must end "Finished release"
cargo test --release         # all tests green (incl. motion_corridor: 2 passed)
```

**B. Freeze + minify + compile-check** (NAME = e.g. v1.22.0-sched)
```
cd /home/tarstars/prj/troll_farm/rust
cp src/main.rs ../cgauto/submissions/NAME.rs
uv run --no-sync python tools/minify.py src/main.rs ../cgauto/submissions/NAME.min.rs
W=$(mktemp -d); cp ../cgauto/submissions/NAME.min.rs $W/cc.rs
rustc --edition 2021 -O $W/cc.rs -o $W/ccbin && echo MIN-OK   # must print MIN-OK
```
(Gotchas: the crate must be edition **2021**, and rustc needs a dot-free filename — hence cc.rs.)

**C. DEBUG build for real-Boss-5 measurement** (never submitted)
```
cd /home/tarstars/prj/troll_farm/rust
W=$(mktemp -d)
sed 's/const DEBUG: bool = false;/const DEBUG: bool = true;/' src/main.rs > $W/dbg.rs
grep -q "DEBUG: bool = true" $W/dbg.rs || echo "FLIP FAILED - STOP"
uv run --no-sync python tools/minify.py $W/dbg.rs $W/dbg.min.rs
cp $W/dbg.min.rs $W/cc.rs && rustc --edition 2021 -O $W/cc.rs -o $W/ccbin && echo DBG-OK
```

**D. Collect real Boss-5 games + measure (the FILTER gate)**
```
cd /home/tarstars/prj/troll_farm
uv run --no-sync python cgauto/collect_debug_games.py $W/dbg.min.rs boss 12
# prints one line per game: "game i/12 <id>: W/L  wood US-BOSS  oppbuild=..."; HTTP 422 => rule 7
uv run --no-sync python cgauto/ramp.py --last 12       # ramp table + verdict vs printed baseline
```
Optional motion check: `uv run --no-sync python cgauto/motion_analyze.py data/boss5_games/boss/game_<id>.raw`
(needs the `.raw`; blocks should stay ≤ ~2%).
Gate (default, per-experiment overrides in §4): **wins ≥ 4/12 AND avg final wood ≥ 45 → go to
arena.** Exactly 3/12 → collect 6 more, go only if ≥ 6/18. Else → revert the edit, record (§8).

**E. Submit to the arena**
```
cd /home/tarstars/prj/troll_farm
uv run --no-sync python cgauto/api_submit.py cgauto/submissions/NAME.min.rs   # "SUBMIT-OK"
```

**F. Verify convergence (the JUDGE)** — wait ≥ 60 min after submit, then:
```
uv run --no-sync python cgauto/cg_rank.py    # read ONLY the ARENA-ROOM line
```
Take two reads ≥ 15 min apart; converged when score moves < 0.1 between them. (A fresh
submission starts low and climbs — an early low read is NOT a verdict.)

**G. Accept or revert** (baseline = frozen best in §0, currently 18.4):
- converged score ≥ baseline + 0.2 → **new frozen best**: update §0, update `api_submit.py`
  default to NAME.min.rs, keep it live.
- within ±0.2 → neutral: keep whichever is live, note the verdict, do NOT update the default
  unless it is the better one.
- ≤ baseline − 0.3 → **revert now**: `api_submit.py cgauto/submissions/<frozen-best>.min.rs`,
  confirm via F, then record.

**H. Record**: update §0 table; append 3-6 lines to `docs/silver-experiment-log.md`
(version, change, boss-gate numbers, arena verdict); update memory if a durable lesson emerged.

## 4. The experiment queue (do IN ORDER)

### T0.1 — Resolve the v1.21.0 verdict  *(do first, no code changes)*
v1.21.0-motion was submitted 2026-07-06 10:35. Run §3.F. Then §3.G against baseline v1.20.0
(117 @ 18.4). Expected: neutral-to-slightly-better (motion cut blocks 4.1%→1.73%, worth ~1-2
wasted turns/game). Whatever the verdict, update §0 and make `api_submit.py`'s default the
winner. Early signal (4 boss games): final wood 49.5 avg vs 38.7 baseline — promising.

### ~~T1 — Validate `decide_sched` (4-troll scale economy)~~ — **EXECUTED 2026-07-06: FAILED, CLOSED**
Gate result: **1/12 wins, avg final wood 13 (range 2-22) vs boss 45 — uniform wood collapse**;
the lone win was on hoarded fruit (10-22 wood). The remembered "3/10 with out-producing wins"
did not reproduce; as configured, decide_sched banks fruit, not wood (~3× below decide_elite).
Dispatch reverted to `decide_elite` the same hour; build+tests re-verified green. **Do not
re-run** (now also in §5 dead ends). The project's biggest open question is resolved: scale
does NOT beat the boss with the current pipeline — proceed to T2.

### T2 — Late-throughput levers on `decide_elite` (one at a time)
These attack the quantified deficit (§1: late farm supply). All constants are in
`rust/src/main.rs` near lines 2108-2126 (grep the name). Standard gates (§3.D); additionally
require the **t300 ramp delta better than −12** (ramp.py prints it; baseline −15.3).

- **★ T2.0  v1.23.0-seedloop (ACTIVE 2026-07-06)** — repair the SEED LOOP. Diagnosis (3 probe
  games + `@TFFEED` instrumentation, now permanent in DEBUG builds): banana seeds stay **0 for
  the whole game** and the farm is **empty (0-1 trees) by t140** — because (a) everyone fells
  bananas at size 2 so nothing ever fruits, and (b) the ANTI-STARVATION fallbacks (both the
  chopper's ~line 2384 and the starter's ~line 2562) bypass `fell_ok` and **eat the protected
  seed trees**. Two older fixes (v1.4.5 seed reserve vs the anti-starvation floor) fight; the
  reserve loses. Fix (one hypothesis, 3 edits): widen `seed_cells` to our-half bananas within
  `chop_r` when farm bananas < K; both anti-starvation fallbacks exclude `seed_cells`. Note
  cc2 fells size-2 and size-4 for the SAME 2 wood, so ripening reserves is ~free. Gate metric
  beyond the standard: banana_seeds > 0 and farm > 2 at t150+ in the `.raw`s (grep @TFFEED).
- **T2.a  late feeder — EXECUTED, INCONCLUSIVE-BY-CONSTRUCTION (2026-07-06)**: with
  `GE_MAX_TROLLS=3, GE_FEEDER_T=150` the feeder **never trained in 12/12 games** — gated by
  `farm_now≥5` (farm is dead: T2.0) AND unaffordable 6/6/6 (post-funding the starter only
  harvests banana/water-apple, so the fruit wallet never refills). REOPEN only after T2.0
  works, and pair the re-run with a funding fix (extend the funding branch condition from
  `want_chopper` to also cover a pending feeder from ~t120).
- **T2.b  v1.24.0-ring3** — STAGED farm growth: keep radius 2 until t120, then radius 3.
  In `decide_elite` find `let farm_r = if econ_b { 3 } else { GE_FARM_R };` (~line 2229) →
  `let farm_r = if state.turn >= 120 { 3 } else { GE_FARM_R };` and widen the cap the same
  way (`farm_cap`: 12 before t120, 20 after). *Why it may work where econ-B (v1.18.0, full-time
  r3) failed:* the tight farm wins the opening; r3 only adds parallel maturation buffer for the
  late game. Radius-2 area (12 cells) is already saturated — density knobs there are exhausted.
- **T2.c  v1.25.0-seed3** — `GE_SEED_RESERVE` 2→3. Only meaningful AFTER T2.0 (protection must
  hold before K matters). Cheapest, weakest theory — run last.

### T3 — Know the actual gatekeepers (analysis, no submission)
Rank ≤99 means beating the humans at ranks ~98-120, who are NOT the boss. Using the
leaderboard access in `cgauto/cg_rank.py` (the codingame package call that prints "(1000
ranked)"), list pseudo+agentId for arena ranks 95-125. Pick 5; play 2 DEBUG games each:
`collect_debug_games.py $W/dbg.min.rs <agentId> 2` (same collector, agentId instead of
`boss`). Run ramp.py on each opponent dir. Deliverable (§8): do they beat us the same way
(late throughput) or differently (denial/raids)? This tells whether T1/T2 gains generalize —
run it in a throttle cooldown or while an arena run converges.

### Phase R — three-layer architecture refactor ★ STRUCTURALLY COMPLETE 2026-07-06 ~15:50
**Final structure:** `src/botmain.rs` (thin: run(), parsing, deciders' shells) + `src/botmain/
{state,motion,tactics,jobs}.rs`. decide_elite = 15 lines: `tactics::plan()` (L1 → 24-field
`Plan` interface) → `jobs::assign_all()` (L2 cascade) → `motion::watchdog()` (L3). Submission
via `tools/bundle.py` (module inliner) → minify.
**Done-criteria:** (1) **500-game equality on the final structure: EQUAL, 0 divergences** ✓
(2) 18 suites / 28 tests ok ✓ (3) minified bundle **92,071 B < 100 KB compiles** ✓
(4) arena hold-check: v1.25.0-layers submitted 15:40, verdict ~16:40 vs contemporaneous
baseline (v1.20.0 drifted to 17.8 @ 15:39; band 17.8-18.6 — the room wanders ±0.4-0.8/hours).
Fallback: resubmit v1.20.0. All artifacts frozen in submissions/ (v1.25.0-ref-deterministic,
v1.25.0-layers).
**R1 status 2026-07-06 ~16:00: harness BUILT + bot DETERMINIZED.** `src/bin/equality.rs`
(black-box: two bot binaries through the CG protocol over sim games, per-turn command-line
equality; opponent = frozen reference binary or WAIT — never lib strategies, they're
nondeterministic). Found + fixed the bot's own nondeterminism (2 HashSet-tie sites:
`free_base`, funding-iron pick → `(score, cell)` keys). Self-play determinism: 50/50 EQUAL.
Reference frozen: `submissions/v1.25.0-ref-deterministic.rs` + `target/refactor/reference_bin`;
VERSION frozen "1.25.0-layers". 500-game baseline run in flight.
**R2 plan (next):** move (verbatim) from main.rs into `src/elite.rs` (lib): State/Tree/Troll
types, Cell, the PLUM..WOOD consts, GE_* consts, helpers (manhattan, ortho_neighbors,
bfs_distances, training_cost, mb_afford, afford_fruit_only, ge_fruit_ty, rh_rand+RH_RNG,
GE_MEM/GE_LASTPOS/GE_CHOSEN_SPEC thread_locals), decide_elite + its motion post-passes,
VERSION. main.rs keeps: parsing (constructs elite::State), debug_log, decide_rhea/decide_sched
(import the moved types). Gate after: cargo build+test, equality vs reference_bin (≥100 seeds),
then the single-file BUNDLER (tools/bundle.py: shim + inlined module → rustc gate → minify gate)
with its own equality run. Then R3 (jobs enum inside elite), R4 (tactics), each harness-gated.
The user's proposal: L1 tactics (phases/specs) / L2 job assignment / L3 motion. Rationale: after
T1's failure the remaining +7-point gap is execution depth — many careful who-does-what-when
changes, which the interleaved ~500-line `decide_elite` makes expensive. L3 already exists
(motion post-passes + corridor tests, blocks 4.1%→1.73%) and proved the carve-out method.
Milestones, each gated:
- **R1 equality harness**: run old vs new decider over ≥1000 simulated games, assert IDENTICAL
  command streams. (This use of the sim is exempt from rule 2 — it checks function equivalence,
  not winrate.)
- **R2 extract L3 motion** behind a module boundary; corridor tests + harness green.
- **R3 extract L2 jobs**: explicit Job enum + assignment fn; harness green (behavior-preserving).
- **R4 L1 tactics** thin layer (phase flags, spec ladder).
- **R5 first behavior-CHANGING L2 policy**: the farm-supply invariant ("no plantable farm cell
  stays empty while a seed is available") as a testable assignment rule → 12-game gate → arena.
- **R6+** iterate L2 policies (dynamic starter role by marginal value; feeder-as-job).

### ★ R6 — the CENTRAL ACTIVITY PLANNER (user directive 2026-07-06; the new main line)
The seeded tie-break (R5.0) restored the accident, not fixed the defect: L2/L3 are SEQUENTIAL
— trolls decide one-by-one in id order, coordinating only via `reserved`/`claimed_drop`
side-effects, so arbitrary order decides outcomes. The fix is a per-turn MANAGER that knows
all tasks and plans all trolls JOINTLY. **Design criterion: SHUFFLE INVARIANCE — permuting
troll order or candidate enumeration must not change the plan** (the objective decides, not
the iteration order; residual objective-ties broken by one canonical rule).

- **R6a — L3 joint move solver.** Input: each troll's goal cell. Output: this turn's MOVE set
  chosen jointly against the verified engine rules (speed ≤ ms, swap-on-cross, block/deadlock
  resolution): maximize total progress, exploit swaps, sequence corridor traffic. Tests: the
  corridor unload (3 trolls / 5 turns) must EMERGE from the objective rather than a hand-coded
  policy (tests/motion_corridor.rs stays green) + NEW property tests: shuffle invariance and
  no-avoidable-self-block on random states.
- **R6b — L2 joint task assignment.** Enumerate the task pool (Fell/Plant/HarvestSeed/
  HarvestFund/Mine/Bank/Park per tactics::Plan), score every (troll, task) pair by marginal
  points per turn (value / ETA), solve the matching exactly (n ≤ 4 trolls → exhaustive ≤ 24
  assignments over a pruned pool). Replaces the priority cascade in jobs::assign_all; the
  branch logic becomes the VALUATION function.
- **Prior art:** decide_sched was a global-greedy scheduler whose ECONOMY tasks were wrong
  (fruit-hoarding, 1/12 wood 13) — salvage the machinery concept, keep the elite economy
  (tight farm, fell-at-2, seed reserve). RHEA search = over-budget/transfer-wall; matching is
  cheap + deterministic. The corridor experiment proved swaps make simple joint plans optimal.
- **Gates (behavior-CHANGING):** unit/property tests → boss 12 → field 6-10 incl. the blowout
  tier (nep7un 113, plcc 115, mikdiet 118, Eagleast 105 — battles.py found −100..−287 losses
  to them) → arena with same-hour bracketing. Success metric: blowout margins shrink and
  win-rate vs 18.7+ rises; killing those blowouts IS the +1.5 to rank ≤99.
- After R6 validates: new stream reference frozen; R5.1 farm-supply invariant becomes a
  VALUATION term (plant value spikes when farm cells empty + seeds available), not a bolt-on.

### T4 — ONLY with the user's explicit go-ahead
- Search bot (RHEA/MCTS over the validated engine within 50 ms) or RL — prior scaffolds exist
  (`decide_rhea`, RL agent) but both are sim-bound (rule 2) and were not competitive.

## 5. Dead ends — tested, closed. DO NOT RETRY

| Idea | Verdict / evidence |
|---|---|
| Seed-reserve widening to mid-map ("seedloop", v1.23.0) | **arena crater 205 @ 15.6 (−2.8)** despite best-ever boss gate — ripening bananas = 3-4-wood gifts for field cc3 choppers (cc2 caps us at 2). Boss↑/field↓ divergence PROVEN 2026-07-06 |
| Late fruit-banking starter ("fruitbank", v1.24.0) | **arena −1.0 (124 @ 17.5)** — from t150 the starter chased 1-pt fruit instead of chop-helping 4-pt fells; field gate (4 games) couldn't see it. 2026-07-06 |
| decide_sched 4-troll scale economy (T1) | **1/12 vs real Boss 5, wood 13 avg (collapse 2-22)** — closed 2026-07-06; fruit-hoarding, no wood pipeline |
| Early feeder 3rd troll @t45 (v1.16.0) | arena neutral-negative: ~126 @ 17.5 vs ~120 @ 17.9 → reverted |
| Full-time big farm r3/cap20/size-3 "econ-B" (v1.18.0) | arena WORSE: ~135 vs ~120 → reverted |
| cc1 cheap chopper (v1.14.0) | worse → reverted |
| 2nd chopper (2 fellers) | starves the farm (real games); the sched fix is 1 super-chopper |
| Fell farm trees at size 3 with cc2 | pointless: yield = min(size, cc); live code fells at 2 (`GE_FARM_FELL=3` is a DEAD const) |
| GE_CHOP_R 5→3 (v1.15.0) | within noise, unshipped |
| Accumulate-only, no early denial | loses the shared-tree race (denial-vs-production frontier memory) |
| `MB_ADAPT_ECON`, `MB_MINE_ALL`, adaptive chopper count, troll cap 5-7, gatherers-first | all no-gain or worse (HANDOFF §8) |
| Tuning economy by SIM winrate | transfer wall: 90.5% sim = 33% real (v1.0.4) |
| Trusting: VERSION labels, submit exit codes, pkg global rank, mid-replay reads | all burned us; see rules 5, and cg-measurement memory |
| More motion micro-optimization | residual 1.73% blocks ≈ swap/noise floor; EV too low |

## 6. Tools & files (what exists, where)

- `rust/src/main.rs` — THE bot (single file, submitted as-is after minify). Deciders:
  `decide_elite` (live), `decide_sched` (T1), `decide_rhea` (unused). Elite knobs ~2108-2126,
  sched knobs ~182-198, main dispatch ~2912.
- `rust/tests/motion_corridor.rs` — locked motion behavior; `cargo test --release`.
- `rust/tools/minify.py in.rs out.rs` — comment/blank stripper (75%); always compile-check output.
- `cgauto/collect_debug_games.py <dbg.min.rs> <boss|agentId> N` — plays REAL games via
  TestSession/play (`playType:["IDE_CODE","BOSS"]`); writes `data/boss5_games/<opp>/game_<id>.{map,log,raw}`
  (`.log` = parsed summary for ramp.py; `.raw` = full stderr for motion_analyze.py).
- `cgauto/ramp.py [dir] [--last N]` — the loss-metric table (baseline printed in its footer).
- `cgauto/motion_analyze.py <game.raw>` — blocks/swaps/speed report.
- `cgauto/api_submit.py [min.rs]` — arena submit (REST; default = frozen best, rule 9).
- `cgauto/cg_rank.py` — ARENA-ROOM rank line (the only trusted scoreboard read).
- `cgauto/submissions/` — frozen artifacts (never edit; add new ones).
- `data/boss5_games/boss/` — 119+ collected real Boss-5 games (the 115-game baseline lives here).
- Session auth: `cgauto/cg_session.txt` (cookies) + TSH inside the scripts. If ALL API calls
  start failing with 4xx, the session likely expired → tell the user; do not brute-force.

## 7. Troubleshooting

- **HTTP 422 / empty games from collect** → throttled (rule 7). Wait ≥15 min. Arena submits
  are throttled separately and usually still work.
- **Minified file fails rustc** → you forgot `--edition 2021` or the filename has a dot.
  If it still fails, the minifier hit a new syntax — compare against `cargo build` (which
  uses the unminified source) and diff the region; do not hand-edit the .min.rs blindly.
- **Rank looks wildly wrong (e.g. 214)** → you read the second (pkg) line; use ARENA-ROOM.
- **Score dropped right after submitting** → normal: fresh submissions re-converge from
  below. Verdict only per §3.F timing.
- **agentId in cg_rank output changed unexpectedly** → someone/something (the :13 cron)
  resubmitted. Check `api_submit.py`'s default is the frozen best; re-run §3.F.
- **Background/long waits get killed** → don't `sleep` inside one command for >20 min; poll
  with repeated short cg_rank.py calls instead.
- **`cargo` says "no such file"** → wrong cwd (rule 8).

## 8. Record-keeping (do this every time, it is how the next session survives)

After each experiment: (1) update the §0 table; (2) append to `docs/silver-experiment-log.md`:
date, version, exact change, boss-gate numbers (wins/12, avg wood, t300 delta), arena verdict
(converged rank@score vs baseline), decision; (3) if a durable lesson emerged, update the
memory files (`late-throughput-ceiling.md`, MEMORY.md index). A verdict that isn't written
down will be re-run by a future agent at full cost.
