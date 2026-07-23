# ARENA QUEUE — the slot never idles

## MEASUREMENT POLICY v2 (2026-07-08, user-designed)
1. **Only DELTAS carry signal.** A verdict is `candidate_reading − baseline_reading`, never an
   absolute level and never a comparison across hours. Time-of-day theories are dropped.
2. **Baseline validity horizon: 5 hours.** Measure the champion once (one convergence), then
   CHAIN candidates back-to-back against that same baseline number until the horizon expires
   or the champion changes — do NOT re-measure the base between candidates (re-measuring
   every pair = 50% slot efficiency; chaining ≈ doubles throughput).
3. **Decision bands calibrated to measured noise** (single-convergence sampling noise ≈ ±1:
   the same champion code converged at 17.6/19.3/19.9 within 12h):
   - delta ≥ +0.5 → KEEP; promotion to champion additionally needs delta ≥ +1.0 once OR
     ≥ +0.5 on two independent convergences.
   - delta ≤ −0.5 → REVERT & reject.
   - |delta| < 0.5 → INCONCLUSIVE: log it, do NOT promote, next candidate submits
     immediately (champion returns to the slot only at chain end or on a −0.5 revert).
4. **Speed first:** verdict at +50 min, no ambiguity extensions unless a goal-gate read is
   involved; the queue must always hold ≥1 READY candidate so the chain never stalls.
5. GOAL GATE unchanged (rank ≤99 twice — a threshold, not a comparison). Slot-ownership and
   commit-verdict-immediately rules unchanged.

**Policy (2026-07-07, user-prompted):** the arena accepts unlimited submissions; only games
(play-API) are budgeted. Therefore: (1) keep a standing ordered queue of ARENA-READY
candidates (built + reviewed + frozen .min.rs); (2) the moment a verdict resolves, the next
candidate submits — especially overnight; (3) gates PRIORITIZE when the queue is full — they
do not serialize when the slot would otherwise idle (the revert rule bounds all downside);
(4) verdict windows are tight: reads at +20/+35/+50 min, decide at +50 unless genuinely
ambiguous (climb-then-fade and flat-low shapes are decidable at +35).

**Slot ownership rule (2026-07-08, after the deny1 double-revert):** one runner owns the slot
from its bracket read until its verdict COMMIT lands in git. The controller may take over only
if BOTH: ≥90 min have passed since the runner's submit AND the arena reads regressed. Runners
commit the verdict the moment it's decided (before reconvergence verification).

**Bracket discipline stands:** every verdict compares against the last converged champion
reading; keep ≥ bracket −0.2; revert = resubmit the champion artifact named below.

## Champion
- v1.43.0-yield (`cgauto/submissions/v1.43.0-yield.min.rs`) — **PROMOTED 2026-07-08
  21:38 MSK**, estimated Gold score **18.4**, rank **116/527**, agentId **6543753**. Bracket was
  v1.42.0-idlefruit at 127/527 @17.4; reads: +20m 139/527 @16.9, +35m 116/527 @18.6, +50m
  116/527 @18.4. Delta **+1.0**, meeting policy v2's single-convergence promotion bar.
  `cgauto/api_submit.py` default now points at this artifact. Goal gate did not fire (116 > 99).
- **Chain-end champion restore (2026-07-09 11:40 MSK, controller):** the candidate chain
  ended (pivot to the ownership DIAGNOSTIC phase — no more candidate submissions). Per policy
  v2's "champion returns to the slot at chain end" rule, the promoted champion v1.43.0-yield
  was resubmitted to the slot (submit id 40971679, SUBMIT-OK). Prior live occupant was the
  post-lateseedhome-revert v1.46.0-splitclaims cold-start (agentId 6544763), which STALLED at
  212/528 @ 15.3 across 3 reads / ~25 min rather than reconverging to its earlier 17.4 KEEP
  level — consistent with room drift (Gold now 528, score bands ~2pt low) plus an incomplete
  cold-start, NOT a code regression (splitclaims passed cargo test + its +0.9 KEEP gate).
  splitclaims' +0.9 was a single convergence (noise ≈ ±1) and never met the +1.0/2×+0.5
  promotion bar, so yield remains the confidently-best resident champion. Working tree +
  champion line now COMMITTED (a0de498, 9b51ddd) — previously uncommitted. Convergence read
  pending (~+50m).
- v1.36.0-race (`cgauto/submissions/v1.36.0-race.min.rs`) — converged band 17.6-20.1,
  rank ~88-121. Promoted 2026-07-07 22:24, superseding v1.28.3-sticky6 (held 19.0-19.2,
  rank ~113, for ~36h). Former default champion until v1.43.0-yield's 2026-07-08 21:38
  promotion. Re-confirmed live 2026-07-08 00:41 after reverting v1.37.0-nanaflow (two stable reads, 111/527 @ 19.3,
  15m17s apart), and AGAIN 2026-07-08 02:37 after reverting v1.38.0-deny1 (two stable reads,
  121/527 @ 17.6, 15m apart — same unmodified code, a lower point in this room's documented
  drift band, not a regression; see verdict log) — arena was not left on a regressed bot
  either time.
- **Arena-slot resolved (2026-07-08 ~02:40):** v1.38.0-deny1's occupation of the slot
  (~00:44-01:47) is now closed out — REVERTED (see verdict log below). The champion has been
  the live arena entry again since a parallel controller's 01:47:07 resubmit; this runner
  independently verified that resubmit's reconvergence (two stable reads, 121/527 @ 17.6).
- **Arena-slot resolved (2026-07-08 03:37):** v1.39.0-sharepen4 (queue #1) verdict is
  **KEEP, AT PARITY** — converged 121/527 @ 17.6, an exact tie with the champion's own
  bracket (also 17.6). Left live in the slot (no revert); `api_submit.py` default stays at
  `v1.36.0-race.min.rs` per the parity rule (candidate is NOT the new champion/default). See
  verdict log below and `docs/silver-experiment-log.md` for the full read sequence.
- **Champion re-baseline (2026-07-08 07:20:53, controller action):** with sharepen4 flat at
  121/527 @ 17.6 for 8 consecutive reads / 3h05m (03:58-07:03, no movement), the controller
  independently resubmitted pure `v1.36.0-race.min.rs`, suspecting the flat 17.6 might mask a
  sharepen4-specific regression. The v1.40.0-roam4 arena-runner (mid-Phase-0) verified the
  resubmission independently (agentId 6542656→6543178) and tracked reconvergence: **stable at
  115/527 @ 19.1** across two reads 86m46s apart (07:53:34, 09:20:20). The v2 policy note itself
  (below, 07:40) confirms this methodology after the fact ("the 07:20 pure-champion resubmission
  IS the fresh baseline; roam4 chains on it") and separately downgrades sharepen4's own
  KEEP-AT-PARITY verdict to **INCONCLUSIVE retroactively** (old ±0.2 threshold was below the
  measured noise floor). INCONCLUSIVE resolves the *label* but not the *mechanism* — whether
  `RACE_SHARE_PEN=4` specifically costs ~1.5pt vs the champion's `=2` remains open; a dedicated
  4→2 isolation retest (chained against one baseline, per v2) would settle it. Full detail in
  `docs/silver-experiment-log.md` ("## v1.40.0-roam4 arena verdict").
- **Arena-slot resolved (2026-07-08 ~10:13):** v1.40.0-roam4 (queue #2) verdict is
  **REVERTED** — baseline 115/527 @ 19.1 (the fresh champion re-baseline above); converged
  199/527 @ 15.5 across a monotonic-fade +20/+35/+50m trajectory (16.1→15.7→15.5), **delta
  −3.6** — decisively past the v2 policy's own −0.5 revert bar (and past the −0.2 margin the
  pre-v2 brief was run under; both frameworks agree). Reverted to `v1.36.0-race.min.rs`
  (10:19:18, SUBMIT-OK); `api_submit.py` default was already this file. Reconvergence confirmed:
  135/527 @ 17.0 across two exact-match reads 14m38s apart (11:02:19, 11:16:57, agentId
  6543474 throughout, after a brief 17.1→16.8 wobble) — arena NOT left on a regressed bot. Note:
  the working *tree*'s consts still carried `GE_CHOP_R=4` post-revert (arena-revert only
  re-submits the frozen artifact); a concurrent gatekeeper hit this contamination and fixed it
  under a new "tree-tracks-champion" rule (`059ee5c`) — see verdict log and
  `docs/silver-experiment-log.md` for both the full read sequence and that cross-reference.

- **Arena-slot resolved (2026-07-08 15:08, controller — runner died to session limit):**
  v1.41.0-nopickloop verdict is **KEEP (+0.5)** — the runner (a3e1a9d) bracketed the champion
  at 135/527 @ 17.0 (11:13-11:33, three stable reads, agentId 6543474), submitted at 11:33:31
  (SUBMIT-OK), then hit the session rate limit at 11:42 — 9 min post-submit, before any
  convergence read. The controller resumed the protocol after the limit reset: converged
  **123/527 @ 17.5** on two exact-match reads (14:56:59, 15:07:55, agentId 6543505), 3.4-3.6h
  post-submit — delta **+0.5** vs bracket, at the v2 KEEP bar. Left live in the slot and
  becomes the CHAINED BASELINE (valid ~5h, until ~20:00) for the next candidate. NOT promoted
  to champion/default (v2 promotion needs +1.0 once or +0.5 twice; this is the first +0.5) —
  `api_submit.py` default stays `v1.36.0-race.min.rs`. Goal gate (≤99) did not fire (123).
- **Arena-slot resolved (2026-07-08 16:33, arena-runner):** v1.42.0-idlefruit (D1 idle-fruit
  band 38) verdict is **INCONCLUSIVE-KEEP (−0.1)** — bracketed the chained baseline at
  123/527 @ 17.5 (agentId 6543505, read 15:42:31), submitted 15:42:40 (SUBMIT-OK). Read
  trajectory (agentId 6543636 from the first read on, confirming landing): +20m 180/527 @ 16.0
  (16:03:06), +35m 129/527 @ 17.3 (16:17:54), +50m 127/527 @ 17.4 (16:32:54) — dip-then-recover-
  then-flatten; last-interval delta only +0.1, below the +0.2/read extension bar, so decided at
  +50m per policy, not extended. **Delta −0.1** vs bracket — inside the v2 `|delta|<0.5`
  INCONCLUSIVE band. The harvest-economy lever (mini-gate: HARVEST+DROP +29% vs the boss pool,
  wood 43.8, 0 crashes) shows no clean effect either direction against the live field pool at
  this single-convergence sampling — consistent with the mini-gate's own caveat that the
  harvest-count lift did not reproduce in its 2-game mikdiet field probe. Left live in the slot
  and becomes the new CHAINED BASELINE (valid ~5h, until ~21:33) for the next candidate. NOT
  promoted — `api_submit.py` default stays `v1.36.0-race.min.rs`. Goal gate (≤99) did not fire
  (best rank this episode: 127).
- **Arena-slot resolved (2026-07-08 21:38, arena-runner):** v1.43.0-yield (D2 task-interference
  / yield-to-urgent) verdict is **KEEP / PROMOTED (+1.0)** — bracketed the chained baseline at
  127/527 @17.4 (agentId 6543636, read 20:47:11), submitted 20:47:20 (SUBMIT-OK). Candidate
  landed as agentId 6543753. Read trajectory: +20m 139/527 @16.9 (dip to −0.5), +35m 116/527
  @18.6 (rebound to +1.2), +50m 116/527 @18.4 (policy read, +1.0). Left live in the slot and
  promoted to default (`cgauto/api_submit.py` now points at `v1.43.0-yield.min.rs`). Goal gate
  did not fire (116 > 99). Detail: `data/candidates/v1.43.0-yield/report.md`.
- **Arena-slot resolved (2026-07-08 22:49, arena-runner):** v1.44.0-harvest-before-fell
  (tree-resource compatibility / harvest-before-fell) verdict is **REJECT / REVERTED (−2.6)** —
  bracketed v1.43.0-yield at 116/527 @18.4 (agentId 6543753, read 22:13), submitted 22:13
  (SUBMIT-OK, submit id 40969606). Candidate landed as agentId 6543779. Read trajectory: +20m
  136/527 @16.9 (−1.5), +35m 182/527 @15.8 (−2.6). Reverted immediately to
  `cgauto/submissions/v1.43.0-yield.min.rs` at 22:49 (submit id 40969730). Restore landed as
  agentId 6543791 by 23:11 (first read 180/527 @16.0, early reconvergence). The narrowed rule
  passed mini-gate, but the live field rejected it; do not requeue this mechanism as a simple
  ripe-tree fell suppression. Detail: `data/candidates/v1.44.0-harvest-before-fell/report.md`.
- **Local gate resolved (2026-07-08 23:39, builder):** v1.45.0-earlyroam
  (opening-only chopper roam widening) verdict is **LOCAL REJECT / NOT SUBMITTED**. Local
  tests, bundle/minify, and equality passed, but the Boss 8 DEBUG mini-gate failed: `0/8`,
  our wood `39.9`, boss wood `53.2`, ramp t300 `-13.4`. It produced the intended early lead
  through t150 but still lost the late burst. Active source restored to v1.43 behavior; do not
  submit or retry this static turn-gated roam widening. Detail:
  `data/candidates/v1.45.0-earlyroam/report.md`.
- **Arena-slot resolved (2026-07-09 00:47, arena-runner):** v1.46.0-splitclaims
  (split fruit-vs-wood tree claims) verdict is **KEEP / NOT PROMOTED (+0.9)**. Bracket:
  restored v1.43.0-yield agentId 6543791 at `151/527 @16.5` (23:55). Submitted 23:56
  (submit id `40969964`). Candidate landed as agentId 6543815. Read trajectory: landing
  `371/527 @11.7`, +20m `169/527 @16.3`, +35m `127/527 @17.4`, +50m `127/527 @17.4`.
  Final delta `+0.9` crosses the KEEP bar but misses the `+1.0` single-read promotion bar.
  Left live as the chained baseline for the next candidate; `api_submit.py` default stays
  `cgauto/submissions/v1.43.0-yield.min.rs`. Goal gate did not fire (`127 > 99`). Detail:
  `data/candidates/v1.46.0-splitclaims/report.md`.

## Queue (ordered; update statuses as they move)
1. **RACE_SHARE_PEN sweep (2→4)** — **CLOSED: KEEP, AT PARITY** (v1.39.0-sharepen4, converged
   121/527 @ 17.6, exact tie with bracket 17.6; left live, not promoted to default). Null
   result — cannot distinguish "mechanism saturated at 2" from "masked by the room's current
   ~2pt night-drift band"; see verdict log.
2. **chop_r 5→4 retest** — **CLOSED: REVERTED** (v1.40.0-roam4, baseline 115/527 @ 19.1,
   converged 199/527 @ 15.5, delta −3.6, monotonic fade not noise). Tightening roam by 1 further
   costs performance on the current R6b planner rather than saving travel — the sweep's premise
   did not hold; `GE_CHOP_R` stays at 5 (champion value); see verdict log.
3. **tree-first-only (nanaflow's safe half)** — re-gate champion-equality UN-WAIVED against
   v1.36.0-race specifically (per the nanaflow post-mortem's own recommendation) to isolate
   it from the diagonal-placement half before restacking both.
4. **diagonal-contest design** — still undesigned; lowest maturity, unchanged last place.
5. **A2 v1.38.0-deny1 — CLOSED, REVERTED** (dead end; filed next to the protection family /
   T-hand). The arena-runner's own read sequence (bracket 111/527@19.3 → +20/+35/+50m
   146/141/135 @ 16.5/16.8/17.0, stable agentId throughout) independently confirmed the
   analyst's 17.0 convergence estimate and the mechanism diagnosis: `DENY_W` collides with
   `race()`'s own contested-tree tie-break (same decision point, bands 70/72), producing
   excessive travel (MOVE:CHOP 1.5-2.6x baseline in 2/3 worst losses). REVERTED — see verdict
   log. Any future denial-weighting retest should target a decision point that doesn't
   collide with `race()`'s own tie-break before trying again.
6. **T-hand line — DROPPED** (post-mortem da574b0: the hand NEVER plants — 4 hauler/1
   tourist/1 idler across 6 games, 34-58% path overlap with the chopper, bill never repaid.
   Residual design note: same-role trolls need a dispersion/exclusivity notion in the
   matcher — filed for the R6 concurrency backlog. Cheap-variant-if-ever: farm-ring-
   restricted forage band.)
7. **Tempo-phase fruit-harvest band** — **RESOLVED 2026-07-08 16:33: ARENA INCONCLUSIVE-KEEP**
   (built as D1 idle-fruit band 38, shipped v1.42.0-idlefruit; bracket 123/527@17.5 →
   converged 127/527@17.4, delta −0.1, inside the v2 noise band; left live as the new chained
   baseline, not promoted to default; see verdict log). Original analysis kept below for
   reference — **UPGRADED from "not urgent" to TOP-RANKED unbuilt
   idea** (analyst loss taxonomy, 2026-07-08 morning, 20-loss champion-specific census —
   supersedes the deny1-contaminated night census this item was filed from). HARVEST-ECONOMY +
   DUAL-ECONOMY shapes together are **45% of all losses, avg margin -63.9** — by far the
   biggest lever measured. Root cause traced in `planner.rs`: under live `Meta::Tempo`,
   `phase_for` never reaches `Phase::Hoard`, so the only "MoveTo any ripe fruit" band (62,
   ~line 270) never fires; fruit is harvested only opportunistically (band 75, BANANA/
   water-APPLE only, gated `!want_chopper`) or via narrow funding bands (58-65). Our own
   HARVEST+DROP totals stay flat 20-90/game regardless of opponent output (91-307). Proposed:
   add a Tempo-active MoveTo-to-ripe-fruit band (~45-48, below chop 70/72 and funding 58-65,
   above chop-help 40/42), any fruit type, whenever free-capacity + no higher candidate.
   Predicted: our HARVEST+DROP rises toward 100+ vs this opponent cluster (mikdiet/
   TheMagicShop/Eagleast/7AM/Haseir/lD); their margin closes from -63.9 toward the OUT-TEMPO
   band (-25). Zero interaction risk with `race()`/`DENY_W` (touches no fell valuation). See
   `docs/silver-experiment-log.md` "## Champion loss taxonomy (2026-07-08 morning)" for the
   full trace and table.
8. **early-roam widening vs delayed-onset (burst-chopper) opponents — LOCAL REJECTED
   2026-07-08 23:39.** Built as `v1.45.0-earlyroam`: true chopper only, Tempo only,
   turns `<=75`, one extra primary-fell roam ring and one-cell own-half margin. Local tests and
   equality passed, but Boss 8 failed (`0/8`, our wood `39.9`, opp wood `53.2`, ramp t300
   `-13.4`). Static turn-gated widening gives early wood but does not survive the late burst.
   Do not submit. If revisiting, use an observed-opponent trigger or a different resource plan,
   not unconditional opening roam. Original rationale: same census; BURST-CHOPPER shape, 10%
   share, avg margin **-103.5**, the worst
   single-shape average, but n=2, thin). Both instances (R4N4R4M4, TheMagicShop) pair an
   opponent troll-count edge (2-3 vs our fixed `GE_MAX_TROLLS=2`) with a near-zero opponent
   CHOP count through turns 1-75 that converts explosively turn ~76-150. Deliberately NOT a
   train-earlier/train-cheaper fix — that re-treads two already-dead ends (T-hand: added troll
   never found a role, reverted -2.2pts; "2nd chopper starves the farm", older). Proposed
   instead: turn-gated only (turns 1-75), loosen `own_half`/`within_roam` (planner.rs ~122-124)
   so our *existing* single chopper claims a wider tree pool while these opponents are
   observably dormant, banking supply before their burst starts. Predicted: our phase-1/2 CHOP
   rises further above the already-measured +16.0 phase-1 lead; their phase-3/4 burst finds a
   smaller pool, narrowing -66/-141 toward the OUT-TEMPO band (-25). If it doesn't pan out, the
   sharper follow-up (relax only when the opponent is *observed* at ~0 fells so far) needs new
   per-game opponent-chop-count state, not just a knob — flagged, not yet designed.
   **Priority note:** rank order for the next FREE queue slot (after #2/chop_r retest and #3's
   re-gate resolve) is **#7 (harvest band) > #8 (early-roam) > #3 (tree-first-only) > #4
   (diagonal-contest)** — #7's weight (28.75, share×margin, HARVEST+DUAL merged) dwarfs
   everything else measured so far, including #3/#4's un-designed, unweighed ideas.

### Design candidates (data-ranked, 2026-07-08 morning)
- **D1 idle-fruit band 38** — the 45%-of-losses lever (harvest-economy): fruit-harvest ONLY on
  otherwise-idle turns (above anti-starvation 30, BELOW chop-help 40 — the fruitbank trap
  inverted). STATUS 2026-07-08 15:20: BUILT (0958ed3, worktree ab5cee13) + review APPROVED
  (band-order invariant proven numerically: sticky 6 ≪ inter-band gap 200k, chop-help worst
  case 3,999,751 > band-38 best case 3,800,006) + reviewer's IMPORTANT fixed (9948578: band 38
  consults `race()`, skips doomed fruit — RED→GREEN test). Re-review, merge, mini-gate, then
  arena CHAINED on the v1.41.0 baseline (123/527 @ 17.5). NOTE: STICKY is 6 (v1.28.3 sweep),
  not 3 as older notes said. STATUS UPDATE 2026-07-08 16:33: ARENA INCONCLUSIVE-KEEP (delta
  −0.1; bracket 123/527@17.5 → converged 127/527@17.4, dip-recover-flatten shape). Left live
  in the slot as the new chained baseline; not promoted to default. See verdict log for the
  full read trajectory.
- **D2 task-interference / yield-to-urgent (user architecture, 2026-07-08):** **RESOLVED
  2026-07-08 21:38: ARENA KEEP / PROMOTED (+1.0)** as `v1.43.0-yield`. Bracket 127/527 @17.4
  → policy read 116/527 @18.4; see verdict log and `data/candidates/v1.43.0-yield/report.md`.
  Original design: L3→L2 feedback edge — when a mover's only path is blocked by a teammate's
  STATIONARY task cell and the mover's band outranks the blocker's, suppress the blocker's
  candidate and re-match that troll.
- **D3 funding-stall robustness — LOCAL REJECTED 2026-07-09 01:13 MSK.** Built as
  `v1.47.0-ripefund`: chopper-funding ripeness anticipation for soon-ripe deficit
  PLUM/LEMON/APPLE. Broad band-57 anticipation cratered `mikdiet` (`0/2`, wood `34-52`);
  the narrowed "final missing fruit only" variant still failed field probes (`6480966` `0/1`,
  wood `78-107`; `6480914` `0/1`, wood `62-106`) and Boss 8 was no better than the v1.46
  watchlist (`1/8`, our wood `44`, ramp t300 `-18.1`). Not submitted. Do not retry simple
  funding ripeness anticipation; any future funding-stall work needs a different mechanism.
- **D4 tentgap — REJECTED 2026-07-08 19:39 MSK. DO NOT BUILD.** The hypothesis "shack cells
  are walkable in the referee but rocks in the bot" was disproven. Official referee source says
  `Cell.isWalkable() == type == GRASS`, and the statement says trolls cannot walk back onto the
  shack after leaving it. Live probe `rust-scratch/tent_probe.rs` confirmed the runtime behavior:
  game `895503881` trained troll `id=2`, moved it from `shack=(9,4)` to `(10,4)`, then issued
  `MOVE 2 9 4`; on the next turn the troll was still at `(10,4)` (`on_shack=false`). Therefore
  do **not** add `'0'`/`'1'` to `walkable`, and do **not** implement the old
  `parse_grid_shacks_walkable` tests. The Sasso_Stark long-route replay must be re-explained as
  normal unwalkable-shack geometry or as another movement/planner issue. Rejected brief retained
  at `data/candidates/v1.44.0-tentgap/brief.md` as a warning.
- **D5 tree-resource compatibility / harvest-before-fell — REJECTED 2026-07-08 22:49 MSK.**
  Built as `v1.44.0-harvest-before-fell`: protect funding/printer/Hoard ripe fruit for nearby
  pure gatherers before wood workers fell that same tree. The first broad version protected all
  idle fruit and failed Boss 8 (`0/8`, t300 `-17.8`); the narrowed version recovered mini-gate
  (`2/8`, t300 `-9.8`, plcc `1/2`) but arena rejected it hard: bracket 116/527 @18.4 →
  +35m 182/527 @15.8, delta `−2.6`. Do not retry as simple fell suppression; any future tree
  compatibility work needs a different mechanism, likely explicit timing/role scheduling rather
  than hiding wood candidates.
- **D6 early-roam widening — LOCAL REJECTED 2026-07-08 23:39 MSK.** Built as
  `v1.45.0-earlyroam`: opening-only true-chopper roam widening, one extra primary-fell ring plus
  one-cell own-half tolerance. Local code gates were clean and frozen artifacts exist, but Boss
  8 failed (`0/8`, our wood `39.9`, opp wood `53.2`, ramp t300 `-13.4`). Not submitted. Static
  turn-gated roam is closed; any future burst-chopper response needs an observed-opponent trigger
  or another mechanism.
- **D7 split fruit-vs-wood tree claims — KEEP / NOT PROMOTED 2026-07-09 00:47 MSK.** Built as
  `v1.46.0-splitclaims`: the matcher now distinguishes `Fruit`, `Wood`, and ordinary `Cell`
  claims. Same-resource claims still conflict; fruit+wood on the same tree is allowed only when
  the fruit worker's ETA is strictly smaller than the wood worker's ETA. This fixes the
  user-observed nearby-apple gatherer/chopper contention without suppressing fells. Local gates
  passed; Boss 8 was PASS-WATCHLIST (`1/8`, our wood `44.0`, ramp t300 `-15.9`), field probes:
  plcc `0/2` but our wood `62` vs opp `92`, mikdiet `2/2` with wood `72-26`. Arena bracket:
  v1.43 restore `151/527 @16.5`; final +50m read `127/527 @17.4`, delta `+0.9`. Left live as
  chained baseline, not promoted to default. Goal gate did not fire (`127 > 99`). Detail:
  `data/candidates/v1.46.0-splitclaims/report.md`.
- **D8 local-printer demotion — LOCAL REJECTED 2026-07-09 01:45 MSK.** Built as
  `v1.48.0-localprinter`: premium printer seed-tree band 52 was restricted to farm-ring
  banana/water-apple sources; distant ripe fruit remained available through idle-fruit band 38.
  Local code gates were clean and artifacts were frozen, but field probes rejected it: Boss 8
  `2/8`, our wood `41.2`, ramp t300 `-13.4`; mikdiet `1/2`, wood `72-51` (worse than v1.46's
  `2/2`, wood `72-26`); plcc `0/1`, wood `72-117`. Not submitted. Active source restored to
  `v1.46.0-splitclaims`. Detail: `data/candidates/v1.48.0-localprinter/report.md`.
- **D9 farm-ring third hand — LOCAL REJECTED 2026-07-09 01:57 MSK.** Built as
  `v1.49.0-farmhand`: `GE_MAX_TROLLS` was re-armed to 3, but the new pure gatherer hand's
  printer and idle-fruit errands were confined to the farm ring. Code gates and equality passed,
  and the third hand actually trained in 7/8 Boss games, but Boss 8 rejected it: `0/8`, our
  wood `46.4`, boss wood `63.8`, ramp t300 `-17.4` versus the stored baseline line `-15.3`.
  Not submitted. Active source restored to `v1.46.0-splitclaims`; simple farm-ring-restricted
  cheap third hand is closed. Detail: `data/candidates/v1.49.0-farmhand/report.md`.
- **D10 late observed threat-fell — LOCAL REJECTED 2026-07-09 02:21 MSK.** Built first as
  broad `v1.50.0-threatfell`, then narrowed as `v1.50.1-latethreat`: a chopper-only band-71
  emergency fell candidate for own-half trees with an enemy wood-capable troll nearby, narrowed
  to `turn >= 150` after broad field probes were weak. Boss 8 improved to `2/8`, final wood
  `46.9-59.6`, t300 `-12.8` versus stored baseline `-15.3`, but field probes rejected it:
  `mikdiet` `2/2` but wood `68-60`, `plcc` `0/2`, wood `30-77` with one `18-97` blowout.
  Not submitted. Active source restored to `v1.46.0-splitclaims`. Detail:
  `data/candidates/v1.50.1-latethreat/report.md`.
- **D11 standing fruit-vs-wood occupancy — LOCAL REJECTED 2026-07-09 MSK.** Root-cause analysis
  of the `v1.50.1` `plcc` blowout found a chopper blocked for ~90 turns by our own fruit worker
  standing on the target tree (`91/265` blocked moves, `34.3%`). Two fixes were tried:
  `v1.51.0-standclaim` made standing fruit/wood same-tree claims conflict, and
  `v1.51.1-fruitstand` made wood candidates skip ripe trees occupied by our own harvest-capable
  worker. Both fixed the block rate, but neither improved field score. Final narrowed result:
  Boss 8 `0/8`, wood `48.1-59.1`, t300 `-11.0`; `plcc` `0/2`, wood `60-91`, block rates
  `0.0%/0.5%`; `mikdiet` `0/2`, wood `80-92`. Not submitted. Active source restored to
  `v1.46.0-splitclaims`. Detail: `data/candidates/v1.51.1-fruitstand/report.md`.
- **D12 late seed-home repair — REJECTED / REVERTED 2026-07-09 MSK.** Built as
  `v1.52.0-lateseedhome`: after t150 under live Tempo, if the farm is below the seed-reserve
  floor (`base_trees < 2`) and banked bananas plus a plantable cell exist, tent PICK/Park is
  raised from band 50 to band 54 so the starter restarts the local farm before walking to
  remote ripe seed trees. Local gates passed. Boss 8: `1/8`, wood `47.9-55.1`, t300 `-7.2`;
  t151-225 farm-zero rate improved in the sample to `43%`. Field candidate probes:
  `plcc 1/2`, `mikdiet 1/2`, `kurigen 1/2`, aggregate score `244.3-238.0`; immediate frozen
  v1.46 comparison was `2/6`, score `232.7-235.2`. Submitted explicitly as
  `cgauto/submissions/v1.52.0-lateseedhome.min.rs` (submit id `40970510`). Bracket:
  `v1.46.0-splitclaims` live at `127/527 @17.4`, agentId `6543815`; landed as agentId
  `6543941`. Arena reads climbed only to `172/528 @16.2`, delta `-1.2`, so it crossed the
  policy revert bar. Reverted to prior live baseline `v1.46.0-splitclaims.min.rs` (submit id
  `40971048`), landed as agentId `6544763` with first fresh-low read `256/528 @14.2`. Active
  source restored to `v1.46.0-splitclaims`; restore tests and equality passed. `api_submit.py`
  default unchanged (`v1.43.0-yield.min.rs`). Detail:
  `data/candidates/v1.52.0-lateseedhome/report.md`.

## Local gate log (not submitted)
- v1.51.1-fruitstand: **LOCAL REJECT / NOT SUBMITTED**. Focused tests, full release suite,
  self/bundled/minified equality passed; minified size `60245` bytes. The mechanism eliminated
  the `plcc` block pattern (`0.0%/0.5%` vs the previous severe `34.3%`) but did not improve
  score: Boss 8 `0/8`, final wood `48.1-59.1`, ramp t300 `-11.0`; `6480966` `0/2`, wood
  `60-91`; `6480914` `0/2`, wood `80-92`. Active source restored to v1.46 behavior; arena was
  not touched. Detail: `data/candidates/v1.51.1-fruitstand/report.md`.
- v1.51.0-standclaim: **LOCAL REJECT / NOT SUBMITTED**. Intermediate broader form. Focused
  tests, full release suite, self/bundled/minified equality passed; minified size `59626` bytes.
  Boss 8 was watchlist-positive (`1/8`, wood `47.4-56.1`, t300 `-8.8`) and `plcc` block rates
  normalized (`3.1%/1.4%`), but field score stayed mixed (`6480966` `0/2`, wood `74-106`;
  `6480914` `1/2`, wood `75-65`). Superseded by the narrower rejected `v1.51.1`.
- v1.50.1-latethreat: **LOCAL REJECT / NOT SUBMITTED**. Focused tests, full release suite,
  self/bundled/minified equality passed; minified size `60930` bytes. Broad v1.50.0 improved
  Boss t300 to `-8.0` but weakened field probes. Narrowed turn-150 form gave Boss `2/8`, wood
  `46.9-59.6`, t300 `-12.8`; field probes rejected it (`6480914` `2/2`, wood `68-60`;
  `6480966` `0/2`, wood `30-77`). Active source restored to v1.46 behavior; arena was not
  touched. Detail: `data/candidates/v1.50.1-latethreat/report.md`.
- v1.49.0-farmhand: **LOCAL REJECT / NOT SUBMITTED**. Focused T-hand/farmhand tests, full
  release suite, self/bundled/minified equality all passed; minified size `59973` bytes. Boss 8
  failed `0/8`, final wood `46.4-63.8`, ramp t75 `+3.1`, t150 `+1.0`, t225 `-5.0`, t300
  `-17.4`. DEBUG summaries confirmed the third hand trained in 7/8 games, so this was an
  engaged mechanism that did not repay the bill. Active source restored to v1.46 behavior; arena
  was not touched. Detail: `data/candidates/v1.49.0-farmhand/report.md`.
- v1.48.0-localprinter: **LOCAL REJECT / NOT SUBMITTED**. Focused tests, full release suite,
  self/bundled/minified equality, and DEBUG smoke passed; minified size `59759` bytes. Boss 8
  was `2/8` but low wood (`41.2-54.6`), mikdiet worsened to `1/2` with opponent wood `51`, and
  plcc remained a blowout (`72-117`). The active source was restored to v1.46 behavior; arena was
  not touched. Detail: `data/candidates/v1.48.0-localprinter/report.md`.
- v1.47.0-ripefund: **LOCAL REJECT / NOT SUBMITTED**. Focused tests passed, full release suite
  passed, and self/bundled/minified equality each returned `EQUAL: 16 games`; minified size
  `61761` bytes. Broad form: Boss 8 `1/8`, wood `47-60`, but field probes cratered
  (`6480914` `0/2`, wood `34-52`). Narrowed frozen form: Boss 8 `1/8`, wood `44-62`, ramp t300
  `-18.1`; field probes still `0/1` each with opponent wood `107`/`106`. Active source restored
  to v1.46 behavior; arena was not touched. Detail:
  `data/candidates/v1.47.0-ripefund/report.md`.
- v1.45.0-earlyroam: **LOCAL REJECT / NOT SUBMITTED**. Focused tests `3 passed`; full release
  suite passed; self/bundled/minified equality each returned `EQUAL: 16 games`; minified size
  `57515` bytes. Boss 8 DEBUG mini-gate failed `0/8`, final wood `39.9-53.2`, ramp t75 `+3.2`,
  t150 `+1.8`, t225 `-4.6`, t300 `-13.4`. Detail:
  `data/candidates/v1.45.0-earlyroam/report.md`.

## Verdict log (newest first)
- v1.52.0-lateseedhome: **REJECT / REVERTED (−1.2)**. Bracket was live
  `v1.46.0-splitclaims` at `127/527 @17.4`, agentId `6543815`. Submitted 2026-07-09 MSK
  (submit id `40970510`), landed as agentId `6543941`. Read trajectory:
  `521/527 @0.0`, `426/527 @10.7`, `261/527 @13.9`, `226/527 @15.1`,
  `211/527 @15.3`, `180/528 @15.9`, `172/528 @16.2`. Final delta **−1.2** crossed the
  v2 revert bar. Reverted to `cgauto/submissions/v1.46.0-splitclaims.min.rs` (submit id
  `40971048`), landed as agentId `6544763` with first fresh-low read `256/528 @14.2`;
  `api_submit.py` default unchanged at `v1.43.0-yield.min.rs`. Detail:
  `data/candidates/v1.52.0-lateseedhome/report.md`.
- v1.46.0-splitclaims: **KEEP / NOT PROMOTED (+0.9)** (bracket restored v1.43.0-yield
  151/527 @16.5, agentId 6543791, read 23:55; submitted 23:56 SUBMIT-OK id 40969964).
  Candidate landed as agentId 6543815. Read trajectory: landing 371/527 @11.7, +20m
  169/527 @16.3, +35m 127/527 @17.4, +50m 127/527 @17.4. Final delta **+0.9** crossed the
  v2 KEEP bar but missed the `+1.0` single-read promotion bar. Left live as chained baseline;
  `api_submit.py` default unchanged (`cgauto/submissions/v1.43.0-yield.min.rs`). Goal gate did
  not fire (`127 > 99`). Detail: `data/candidates/v1.46.0-splitclaims/report.md`.
- v1.44.0-harvest-before-fell: **REJECT / REVERTED (−2.6)** (bracket v1.43.0-yield
  116/527 @18.4, agentId 6543753, read 22:13; submitted 22:13 SUBMIT-OK id 40969606).
  Candidate landed as agentId 6543779. Read trajectory: +20m 136/527 @16.9, +35m 182/527
  @15.8. Final delta **−2.6** crossed the v2 revert bar. Reverted to
  `cgauto/submissions/v1.43.0-yield.min.rs` at 22:49 (submit id 40969730); restore landed as
  agentId 6543791 by 23:11. Detail:
  `data/candidates/v1.44.0-harvest-before-fell/report.md`.
- v1.43.0-yield: **KEEP / PROMOTED (+1.0)** (bracket 127/527 @17.4, agentId 6543636, read
  20:47:11; submitted 20:47:20 SUBMIT-OK). Candidate landed as agentId 6543753. Read trajectory:
  +20m 139/527 @16.9, +35m 116/527 @18.6, +50m 116/527 @18.4. Final delta **+1.0** meets the
  v2 single-convergence promotion bar. Left live in the slot; `api_submit.py` default updated to
  `cgauto/submissions/v1.43.0-yield.min.rs`. Goal gate did not fire (116 > 99). Detail:
  `data/candidates/v1.43.0-yield/report.md`.
- v1.42.0-idlefruit: **INCONCLUSIVE-KEEP (−0.1)** (bracket 123/527 @17.5, agentId 6543505,
  read 15:42:31; submitted 15:42:40 SUBMIT-OK). Read trajectory: +20m 180/527@16.0 (16:03:06,
  agentId 6543636 — confirms landing), +35m 129/527@17.3 (16:17:54), +50m 127/527@17.4
  (16:32:54, agentId 6543636 throughout) — dip-then-recover-then-flatten; last-interval delta
  only +0.1 (below the +0.2/read extension bar), decided at +50m per policy, not extended.
  **Delta −0.1**, inside the v2 INCONCLUSIVE band (|delta|<0.5). D1 (idle-fruit band 38, the
  45%-of-losses harvest-economy lever; mini-gate: wood 43.8, HARVEST+DROP +29% vs the boss
  pool, 0 crashes) shows no clean arena effect either direction against the live field pool at
  this single-convergence sampling — consistent with the mini-gate's own flagged caveat that
  the harvest-count lift did not reproduce in its 2-game mikdiet field probe. Left live in the
  slot as the new chained baseline; `api_submit.py` default unchanged (`v1.36.0-race.min.rs`).
  Goal gate (≤99) did not fire (best rank: 127). Detail:
  `data/candidates/v1.42.0-idlefruit/report.md`.
- v1.41.0-nopickloop: **KEEP (+0.5)** (bracket 135/527 @17.0; submitted 11:33:31 SUBMIT-OK;
  runner killed by session rate limit at 11:42, controller took the verdict reads after the
  14:50 reset: 123/527 @17.5 twice, exact match, 14:57/15:08 — +0.5 at the v2 KEEP bar).
  The corridor PICK/DROP livelock fix (user replay finding #4) rides along wood-neutral
  (mini-gate #3: wood 51.2) and is insurance-class for rare corridor maps. Left live =
  chained baseline; default unchanged (first +0.5, promotion needs a second). Slot-continuity
  note: the runner's 3 bracket reads + the controller's 2 verdict reads bound the same
  convergence; no reads were possible in the 11:42-14:50 limit window (arena had 3.4h to
  converge — decided on the post-reset plateau, consistent with policy v2 deltas-only).
  Detail: `data/candidates/v1.41.0-nopickloop/report.md`.
- v1.40.0-roam4: **REVERTED** (baseline 115/527 @19.1 — a fresh champion re-baseline the
  controller triggered mid-episode, not this candidate's own bracket read; see the "Champion
  re-baseline" bullet above for that sub-episode's own detail — converged 199/527 @15.5 across
  a monotonic-fade +20/+35/+50m trajectory, 16.1→15.7→15.5, no rebound at any point, decided
  at +50m per the brief, not ambiguous. **Delta −3.6**, decisively past both the pre-v2 brief's
  −0.2 keep-margin AND the v2 policy's own −0.5 revert bar (policy landed mid-episode, commit
  73d3c10 07:32:50 — this verdict is robust to both framings). `GE_CHOP_R` 5→4 costs performance
  rather than saving travel; the roam-radius-tightening hypothesis is not supported at this
  planner generation either (the cascade-era radius-3 "within noise" verdict already didn't
  transfer, and radius 4 now measures as a clean loss, not a null result). Reverted to
  `v1.36.0-race.min.rs` (`api_submit.py` default already pointed there — no edit needed);
  reconvergence confirmed at 135/527 @17.0 (two exact-match reads 14m38s apart, 11:02:19/
  11:16:57, agentId 6543474, after a brief 17.1→16.8 wobble) — arena not left on a regressed
  bot. Goal gate (≤99) did not fire (best rank this episode: 115/527). Mid-episode process note: the
  runner's original Phase-0 night-trough-wait loop (8 flat reads, 121/527@17.6, 03:58-07:03) was
  superseded by a controller redirect at 07:20-07:21 to bracket off an independently-verified
  fresh champion resubmission instead (agentId 6542656→6543178, converged 115/527@19.1); the
  "sharepen4 masked regression" question this raised is flagged, not resolved (see above). Full
  detail in `docs/silver-experiment-log.md` ("## v1.40.0-roam4 arena verdict") and
  `data/candidates/v1.40.0-roam4/report.md`.
- v1.39.0-sharepen4: **KEEP, AT PARITY** (bracket 121/527 @17.6, re-confirmed independently
  after the deny1 revert; converged 121/527 @17.6 across a flat +20/+35/+50m trajectory,
  17.4→17.6→17.6, decided at +50m, not ambiguous — exact tie with bracket, 0.0pt delta).
  `RACE_SHARE_PEN` 2→4 (+ `DENY_W` parked at 0) is a null result in this room right now. Left
  live in the slot; `api_submit.py` default unchanged (`v1.36.0-race.min.rs`, parity rule).
  Goal gate (≤99) did not fire. Full detail in `docs/silver-experiment-log.md` and
  `data/candidates/v1.39.0-sharepen4/report.md`.
- v1.38.0-deny1: REVERTED (bracket 111/527 @19.3; converged 135/527 @17.0 across a stable
  +20/+35/+50m trajectory, 16.5→16.8→17.0, a −2.3pt shortfall vs the −0.2pt keep bar, not
  ambiguous — independently corroborated by the analyst's parallel `battles.py` census
  (identical 17.0/~135) and the mechanism diagnosis: `DENY_W` collides with `race()`'s own
  contested-tree tie-break, same bands 70/72, causing excessive travel. Process note: a
  parallel "controller" resubmitted the champion at 01:47:07 believing this runner had gone
  silent — it had not (mid-flight on the brief's own explicitly-allowed +65m confirmatory
  read); the +65m read (353/527@12.0, agentId 6542647) is discarded as contaminated — a
  different agentId, i.e. the freshly-resubmitted champion's own cold-start noise, not deny1.
  Runner/analyst/controller independently reached the same REVERT conclusion — a coordination
  gap, not a disagreement. Champion reconvergence verified by this runner (two stable reads,
  121/527 @ 17.6, 15m apart) — a lower level than the most recent 19.3 mark but the same
  unmodified code, consistent with this room's documented score drift, not a regression. Goal
  gate (≤99) did not fire. Full detail in `docs/silver-experiment-log.md`
  ("## v1.38.0-deny1 arena verdict") and `data/candidates/v1.38.0-deny1/report.md`.
- v1.37.0-nanaflow: REVERTED (bracket 103/527 @19.9; converged climb-then-flatten at
  142/527 @16.6-16.7, 3.2-3.3pts below bracket, decided at +50m, not ambiguous; reverted to
  v1.36.0-race at 23:50:11, reconverged 111/527 @19.3 confirmed by two stable reads; goal
  gate ≤99 did not fire; analyst hypothesis: tree-first re-ranking may conflict with the
  race-check's doomed-target steering, or diagonal-placement may congest differently under
  real-field map geometry than the boss-gate's map pool — champion-equality gate should be
  un-waived against v1.36.0-race if either sub-mechanism is revisited; full detail in
  `docs/silver-experiment-log.md` and `data/candidates/v1.37.0-nanaflow/report.md`).
- v1.36.0-race: KEPT — new CHAMPION (doomed-target race check + winnable-contest join;
  arena converged ~19.9-20.1 vs 18.6 bracket, steady-climb-to-flat, +1.3-1.5 pts; largest
  single-candidate jump of the T-hand/protection cycle; boss/field probe waived per the
  idle-slot policy; `api_submit.py` default updated; full detail in
  `docs/silver-experiment-log.md` and `data/candidates/v1.36.0-race/report.md`).
- v1.35.0-thand: REVERTED (arena ~16.8 fading at +35m vs 19.0 bracket; hand trains 6/6 but
  doesn't pay its 9-fruit bill — analyst question queued).
- v1.28.3-sticky6: superseded 2026-07-07 by v1.36.0-race after holding 19.0-19.2 for ~36h.

## 2026-07-16 — current Legend slot

- **2026-07-17 behavior-identical slim A/A: KEEP / NEW PACKAGING BASELINE.**  Full-size agent
  `6556873` was frozen at rank 21/104 @24.5.  Slim submission `41005161` landed as agent
  `6557204`, read 23.3 at +20 and +35, then converged to rank 24/104 @24.2 at +50 and held 24.2
  through six consecutive closing reads.  Its 160 finished battles by +52 were comparable to
  the full-size reference's 167-game sample.  Delta -0.3 is inside the `|delta|<0.5` noise band;
  keep slim and default `api_submit.py` to the arena-validated 62,725-byte artifact.  This is a
  packaging verdict only; strategy is unchanged.  Full record:
  `data/analysis/live-agent-6553250/arena-retry-2026-07-17.md`.

- **2026-07-17 pre-seed + secure-orchard-coverage retry: PROMOTED (+3.0 to +3.3).**  Exact-source
  A/A submit `41004754` landed as agent `6556775`, received 67 battles, and reconverged from a
  21.1 pre-reset reading to 21.1 with a 20.8 confirming read.  Candidate submit `41004799`
  landed as agent `6556873` and later held rank 23/104 Legend @24.1 on two authoritative reads
  after 161 listed battles.  This beats the fresh 20.8-21.1 bracket by +3.0 to +3.3.  The
  full-size candidate remained live through the later slim A/A; the default now points at its
  arena-validated behavior-identical slim encoding.  The
  nominal +20/+35/+50 reads were missed; the decisive read was around +102m but inside the
  five-hour bracket horizon.  Full record:
  `data/analysis/live-agent-6553250/arena-retry-2026-07-17.md`.
  A later closing read reached rank 20/104 @24.4.

- **pre-seed + secure-orchard-coverage stack: INCONCLUSIVE / ROLLED BACK.** Exact live bracket agent
  `6553250`: rank 6/104 Legend @26.3. Candidate submit `41002151` landed as agent `6555355`,
  peaked transiently at rank 11 @25.3, then read rank 34 @23.3 at +20m. Standing policy
  triggered rollback. Exact artifact restored via submit `41002271`, agent `6555394`, but the
  same-code A/A control reached only 16.1 at +20m and 19.9 at +35m versus its prior 26.3.
  Uneven game waves plus an `URLError` indicate degraded platform capacity; no causal candidate
  verdict is possible. Default remained exact live. Pause writes until normal same-code
  convergence; see `data/analysis/live-agent-6553250/arena-verdict-2026-07-16.md`.
