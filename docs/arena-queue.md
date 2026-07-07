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
- v1.36.0-race (`cgauto/submissions/v1.36.0-race.min.rs`) — converged band 19.9-20.1,
  rank ~88-103. Promoted 2026-07-07 22:24, superseding v1.28.3-sticky6 (held 19.0-19.2,
  rank ~113, for ~36h). `cgauto/api_submit.py` default now points at this candidate.

## Queue (ordered; update statuses as they move)
1. **v1.37.0-nanaflow** — READY (built + reviewed SPEC-pass; submits next). Note: its
   champion-equality gate target may need reconsideration now that v1.36.0-race (not
   sticky6) is champion — flag for the analyst.
2. **A2 v1.38.0-deny1** — TO BUILD (3-line denial-weight probe, DENY_W=1).
3. **diagonal-contest** — DESIGN (the "join raids on our pocket trees" split-aware defense;
   strictly-gated protection-family sub-candidate).
4. **T-hand line — DROPPED** (post-mortem da574b0: the hand NEVER plants — 4 hauler/1
   tourist/1 idler across 6 games, 34-58% path overlap with the chopper, bill never repaid.
   Residual design note: same-role trolls need a dispersion/exclusivity notion in the
   matcher — filed for the R6 concurrency backlog. Cheap-variant-if-ever: farm-ring-
   restricted forage band.)

## Verdict log (newest first)
- v1.36.0-race: KEPT — new CHAMPION (doomed-target race check + winnable-contest join;
  arena converged ~19.9-20.1 vs 18.6 bracket, steady-climb-to-flat, +1.3-1.5 pts; largest
  single-candidate jump of the T-hand/protection cycle; boss/field probe waived per the
  idle-slot policy; `api_submit.py` default updated; full detail in
  `docs/silver-experiment-log.md` and `data/candidates/v1.36.0-race/report.md`).
- v1.35.0-thand: REVERTED (arena ~16.8 fading at +35m vs 19.0 bracket; hand trains 6/6 but
  doesn't pay its 9-fruit bill — analyst question queued).
- v1.28.3-sticky6: superseded 2026-07-07 by v1.36.0-race after holding 19.0-19.2 for ~36h.
