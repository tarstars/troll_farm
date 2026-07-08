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

## Queue (ordered; update statuses as they move)
1. **RACE_SHARE_PEN sweep (2→4)** — **CLOSED: KEEP, AT PARITY** (v1.39.0-sharepen4, converged
   121/527 @ 17.6, exact tie with bracket 17.6; left live, not promoted to default). Null
   result — cannot distinguish "mechanism saturated at 2" from "masked by the room's current
   ~2pt night-drift band"; see verdict log.
2. **chop_r 5→4 retest** — PROMOTED. Orthogonal travel-reduction lever in the same
   "cut waste" family as the race-check's proven win; no fell-valuation interaction risk.
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
  inverted). After pickloop.
- **D2 task-interference / yield-to-urgent (user architecture, 2026-07-08):** L3→L2 feedback
  edge — when a mover's only path is blocked by a teammate's STATIONARY task cell and the
  mover's band outranks the blocker's, suppress the blocker's candidate and re-match that
  troll (it plants-aside/parks-off-path; resumes next turn automatically). Also absorbs the
  same-role dispersion note. Test: corridor, picker-on-tree vs banking chopper.
- **D3 funding-stall robustness** — 2nd-troll training at t77-89 on fruit-poor draws (60-90
  turns of farm=0); design direction: ripeness-anticipation over wider roaming.

## Verdict log (newest first)
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
