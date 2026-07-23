# Troll Farm — Current Conclusions (2026-07-09)

Standing synthesis of what we've concluded. Distinct from the blow-by-blow narrative in
`docs/silver-experiment-log.md` and the live queue in `docs/arena-queue.md`. Update the date
when you revise.

## Status
- **Champion:** v1.43.0-yield (task-interference / yield-to-urgent), ~18.4, rank ~116–125 Gold.
- **Goal:** rank ≤99 (verified twice), ≈ score 19.7. **UNMET.** Best ever: 88 @ 20.1
  (v1.36.0-race, read once). The gap (~+1.5) has resisted every economy change; only
  execution cuts have moved it.

## Conclusion 1 — the band's law: EXECUTION waste-cuts transfer; ECONOMY rebalances don't
The most verdict-backed conclusion of the project. Every arena gain has been an
execution/coordination waste-cut; every economy/production rebalance has fizzled or cratered.
- **Wins (execution):** race check / doomed-target skip **+1.3**; yield-to-urgent joint task
  interference **+1.0**; joint move solver **+0.7**; corridor livelock fix **+0.5**.
- **Fizzles/craters (economy):** idle-fruit −0.1, harvest-before-fell −2.6, earlyroam (boss
  0/8), seedloop −2.8, fruitbank −1.0, reserve −2, ownership governor +0.2 (neutral), plus a
  string of local rejects (ripefund / localprinter / farmhand / latethreat / standclaim /
  lateseedhome).
- **Mechanism (hypothesis):** at this band our economy is already ~saturated; growing or
  preserving the "pie" feeds the opponent's better late engine as much as ours. The only pure
  gain is cutting our OWN wasted motion/decisions — that doesn't help the opponent.

## Conclusion 2 — "total map value ownership" is KILLED as a lever (inert, not a crater)
Built as v1.53.0-pressurefarm (Orange-gated farm governor: clamp farm cap / release seed
reserve / liquidate exposed farm trees, but only when an opponent actually threatens our own
farm value). **Three independent measurements converged on inert:**
1. **Baseline corpus (36 labeled games):** the exposed-value signal does NOT predict losses —
   `own_half_exposed@t150` averaged WIN 67.6 > LOSS 55.6 (*reversed*). It's confounded with
   farm-size (a bigger active farm ⇒ more value in play ⇒ correlated with *winning*), so it
   measures "how much we have," not "how much is at risk."
2. **Measurement gate (12 games):** the Yellow→Orange fix held — the governor is active only
   ~8% of mid-late turns and wood didn't crater (48.8) — SAFE, but no win benefit.
3. **Arena (5 reads):** neutral +0.2 (17.4 → 17.6).

So it is the FIFTH "pie" idea — but the first NON-cratering one (the earlier four all went
negative). The program is **parked**; the follow-ons (dynamic seed reserve v2, raid response)
are moot. One durable design win survives: the Yellow→Orange fix (gate the clamp on
`created_exposed>0`, our own threatened farm trees, NOT `own_half_exposed>0`, static geometry)
is the difference between a crater and inert — it made the trigger genuinely opponent-threat-
driven. Threat-driven-but-useless still teaches us the signal itself is wrong.

## Conclusion 3 — aggregate metrics don't separate wins from losses; go position-level
The methodological conclusion, and the reason the ownership program found no signal:
correlating whole-game aggregate metrics (exposed value, wood, etc.) with win/loss does NOT
cleanly separate them — the corpus is the proof (the intended loss-predictor *reversed*). Full
games are too noisy and confounded. To find the CAUSAL principles that decide games we need
position-level analysis with known outcomes — the **etudes** subproject.

## Etudes subproject — design state (in progress, not yet spec'd)
- **Approach A: exact / provable on small constructed positions** (a micro-tablebase), chosen
  over approximate self-play — because "proof of verdict" only means something when it is a
  checkable forcing line, and provable micro-positions are the cleanest way to isolate the
  principles the ownership heuristic missed.
- **Key subtlety:** Troll Farm is a SIMULTANEOUS-move game, so "who wins under ideal play" is
  in general a mixed-strategy *probability*, not a deterministic winner.
- **Proposed resolution (recommended; pending final user confirmation):** restrict the etude
  database to FORCED outcomes — positions where one side can guarantee a strictly better final
  score against ANY opponent play. Proof = a strategy that beats the opponent's best response
  (max-min). Contested/equilibrium positions are excluded or flagged "unresolved," never given
  a false crisp verdict.
- **Components:** (1) situation format (a `GameState` snapshot + horizon), (2) viewer, (3)
  etude DB `{situation, verdict, proof}`, (4) the forced-outcome solver (the crux). Builds on
  the existing deterministic sim engine (`rust/src/game/engine.rs`) + `mapgen` + the black-box
  equality harness.

## Open levers (ranked)
1. **Etudes (research)** — the position-level tool to find what actually decides games;
   highest long-term value given Conclusion 3.
2. **Sasso long-path re-diagnosis (execution class)** — the 200+ wasted-turn paths on the
   lake+tent+boulder map are REAL, but my walkability theory was wrong (shacks are NOT
   walkable); the true cause is un-found. If it's a routing/valuation bug, it's the transfer
   class (Conclusion 1) and the best near-term arena bet.
3. **Aggressive Tempo fruit-harvest band** — the biggest loss-*weight* lever (28.75), but only
   the timid idle-only version was tried (−0.1); economy-class, so low confidence.

## Closed lines (do not re-open without a NEW mechanism)
- **Pie family 0-for-5:** protection / seedloop / fruitbank / reserve (all negative) +
  ownership (neutral).
- **3-troll scale:** lemon wall (a timing artifact) + T-hand (the added troll never found a
  role, reverted).
- **Static turn-gated behavior:** earlyroam (boss 0/8), lateseedhome (−1.2) — triggers must be
  observed-state, never turn-number.
- **D4 tentgap:** shacks are NOT walkable (disproven by live probe game 895503881).
- **Denial weighting:** DENY_W collides with `race()`'s own tie-break (deny1 −2.3).

## Process notes
- **Policy v2:** only base→candidate DELTAS carry signal (baseline valid ~5h, chain candidates,
  ±0.5 bands, promote at +1.0 once or +0.5 twice). Absolute scores drift ±1–2 over hours on
  identical code.
- **Subagent pipeline** (builder → review → gate → arena): the reviewer caught the pie trap
  BEFORE the arena, making the ownership verdict cheap and clean. The gate's instrumented
  telemetry (not just wood) is what let us see "safe but useless" rather than guess.
- **Anthropic API "Overloaded"** can kill subagents mid-task; the controller can run
  collect / gate / arena INLINE (the CodinGame API works from the main thread even when
  subagent inference is throttled).
