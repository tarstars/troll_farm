# ARENA QUEUE — the slot never idles

**Policy (2026-07-07, user-prompted):** the arena accepts unlimited submissions; only games
(play-API) are budgeted. Therefore: (1) keep a standing ordered queue of ARENA-READY
candidates (built + reviewed + frozen .min.rs); (2) the moment a verdict resolves, the next
candidate submits — especially overnight; (3) gates PRIORITIZE when the queue is full — they
do not serialize when the slot would otherwise idle (the revert rule bounds all downside);
(4) verdict windows are tight: reads at +20/+35/+50 min, decide at +50 unless genuinely
ambiguous (climb-then-fade and flat-low shapes are decidable at +35).

**Bracket discipline stands:** every verdict compares against the last converged champion
reading; keep ≥ bracket −0.2; revert = resubmit the champion artifact named below.

## Champion
- v1.36.0-race (`cgauto/submissions/v1.36.0-race.min.rs`) — converged band 19.3-20.1,
  rank ~88-111. Promoted 2026-07-07 22:24, superseding v1.28.3-sticky6 (held 19.0-19.2,
  rank ~113, for ~36h). `cgauto/api_submit.py` default points at this candidate. Re-confirmed
  live 2026-07-08 00:41 after reverting v1.37.0-nanaflow (two stable reads, 111/527 @ 19.3,
  15m17s apart) — arena was not left on a regressed bot.
- **Arena-slot note (analyst, 2026-07-08 ~01:24):** the champion is the standing default and
  designation, but it is **not currently the live arena entry** — v1.38.0-deny1 (below) has
  occupied the slot since ~00:44-00:48, per the queue-never-idles policy. `battles.py`/
  `cg_rank.py` reads during this window reflect deny1, not the champion; see the analyst
  census in `docs/silver-experiment-log.md` ("Analyst census on the race champion,
  2026-07-08 night") for full detail and the structural note that there is no read-API path
  to recover a superseded agent's battle history once a newer candidate takes the slot.

## Queue (ordered; update statuses as they move)
1. **RACE_SHARE_PEN sweep (2→4)** — PROMOTED to top (analyst re-rank 2026-07-08 night).
   Tunes the one mechanism with a proven, large positive field result (the race-check
   itself); lowest interaction risk of the remaining ideas.
2. **chop_r 5→4 retest** — PROMOTED. Orthogonal travel-reduction lever in the same
   "cut waste" family as the race-check's proven win; no fell-valuation interaction risk.
3. **tree-first-only (nanaflow's safe half)** — re-gate champion-equality UN-WAIVED against
   v1.36.0-race specifically (per the nanaflow post-mortem's own recommendation) to isolate
   it from the diagonal-placement half before restacking both.
4. **diagonal-contest design** — still undesigned; lowest maturity, unchanged last place.
5. **A2 v1.38.0-deny1** — STATUS CORRECTED (was stale "TO BUILD"): already builder-complete
   since 2026-07-07 22:22 and **currently LIVE in the arena** (submitted by a concurrent
   arena-runner ~00:44-00:48 on 2026-07-08, per the queue-never-idles policy). Analyst
   monitoring (read-only, ~40 min, see silver-experiment-log.md) found it **converged at
   score 17.0 / rank ~134-136** — a 2.3-3.1 pt regression vs the champion's own band, in a
   40-game battles.py sample that is properly matched (not a still-climbing transient).
   Loss-replay decode of the 3 worst losses found our own MOVE:CHOP ratio running 1.5-2.6x
   the historical baseline in 2 of 3 — suggestive of DENY_W adding wasted travel by
   colliding with the race-check's own contested-tree tie-break (same decision point, bands
   70/72). DEMOTED to last priority pending the arena-runner's actual verdict; if reverted as
   trending, file next to the protection family / T-hand as a closed dead end.
6. **T-hand line — DROPPED** (post-mortem da574b0: the hand NEVER plants — 4 hauler/1
   tourist/1 idler across 6 games, 34-58% path overlap with the chopper, bill never repaid.
   Residual design note: same-role trolls need a dispersion/exclusivity notion in the
   matcher — filed for the R6 concurrency backlog. Cheap-variant-if-ever: farm-ring-
   restricted forage band.)
7. **NEW, filed (not urgent):** mlomb-style fruit-harvest/bank win pattern (low chop count,
   high HARVEST+DROP volume) — a loss mechanism not previously catalogued; needs a dedicated
   look once a champion-specific census is unblocked (analyst finding, 2026-07-08 night).

## Verdict log (newest first)
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
