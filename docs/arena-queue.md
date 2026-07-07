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
- v1.28.3-sticky6 (`cgauto/submissions/v1.28.3-sticky6.min.rs`) — band 19.0-19.2, rank ~113.

## Queue (ordered; update statuses as they move)
1. **v1.36.0-race** — READY (built, reviewed, merged; boss/field gate WAIVED for tonight's
   idle slot — pure waste-cut, no pie risk; diagnostic probe games optional tomorrow).
2. **v1.37.0-nanaflow** — BUILDING (banana tree-first + diagonal placement + bank-excess).
3. **A2 v1.38.0-deny1** — TO BUILD (3-line denial-weight probe, DENY_W=1).
4. **diagonal-contest** — DESIGN (the "join raids on our pocket trees" split-aware defense;
   strictly-gated protection-family sub-candidate).
5. **T-hand.3** — PARKED IDEA (needs the "does the trained hand actually plant?" analyst
   answer from the T-hand revert data before any retry).

## Verdict log (newest first)
- v1.35.0-thand: REVERTED (arena ~16.8 fading at +35m vs 19.0 bracket; hand trains 6/6 but
  doesn't pay its 9-fruit bill — analyst question queued).
- v1.28.3-sticky6: CHAMPION (held 19.0-19.2 for ~36h).
