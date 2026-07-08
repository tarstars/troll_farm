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
- v1.36.0-race (`cgauto/submissions/v1.36.0-race.min.rs`) — converged band 17.6-20.1,
  rank ~88-121. Promoted 2026-07-07 22:24, superseding v1.28.3-sticky6 (held 19.0-19.2,
  rank ~113, for ~36h). `cgauto/api_submit.py` default points at this candidate. Re-confirmed
  live 2026-07-08 00:41 after reverting v1.37.0-nanaflow (two stable reads, 111/527 @ 19.3,
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
7. **Tempo-phase fruit-harvest band** — **UPGRADED from "not urgent" to TOP-RANKED unbuilt
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
8. **NEW — early-roam widening vs delayed-onset (burst-chopper) opponents** — second-ranked
   unbuilt idea (same census; BURST-CHOPPER shape, 10% share, avg margin **-103.5**, the worst
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
  not 3 as older notes said.
- **D2 task-interference / yield-to-urgent (user architecture, 2026-07-08):** L3→L2 feedback
  edge — when a mover's only path is blocked by a teammate's STATIONARY task cell and the
  mover's band outranks the blocker's, suppress the blocker's candidate and re-match that
  troll (it plants-aside/parks-off-path; resumes next turn automatically). Also absorbs the
  same-role dispersion note. Test: corridor, picker-on-tree vs banking chopper.
- **D3 funding-stall robustness** — 2nd-troll training at t77-89 on fruit-poor draws (60-90
  turns of farm=0); design direction: ripeness-anticipation over wider roaming.
- **D4 tentgap (user replay finding #5, 2026-07-08): shack cells are WALKABLE in the referee
  but rocks in the bot's parse_grid** — phantom wall: 24-vs-2-step BFS divergence on the
  Sasso_Stark map (game 895493013), 13 cross-wall treks ≈ 200+ wasted troll-turns (~1/3 of
  locomotion) in one game. Fix = 2-line walkability + never-PLANT-on-shack +
  never-PARK-on-shack guards; brief READY at `data/candidates/v1.44.0-tentgap/brief.md`.
  PRIORITY: build immediately after D2 (execution waste-cut class — the class that
  transfers; likely ranks ABOVE D3).

## Verdict log (newest first)
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
