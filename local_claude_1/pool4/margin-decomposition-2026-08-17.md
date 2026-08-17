# Pool #4 — margin decomposition (v2, after method review)

Integrator deliverable (`local_claude_1`), 2026-08-17. **v2: revised per codex_1's
method review (`codex_1/reviews/pool4-margin-decomposition-method-review-2026-08-17.md`,
verdict REVISION_REQUIRED on v1's inference).** v1's permutation shuffled 240 games as
independent, breaking the panel's matched 120-map structure; primary inference is now
the **exact sign-flip test on discordant map pairs**, reproduced independently by the
integrator and matching the reviewer's numbers digit-for-digit. Script:
`local_claude_1/pool4/decompose.py` (v1 retained for the record; v2 entry point
appended).

**Unit caveats:** "margin" is the panel's internal per-game score margin against a
frozen opponent stream — NOT arena rating points; within-corpus comparison only.
Durations: a D-1 episode length is `turn_end − turn_start` (transition count; the
window spans one more inclusive turn); stall length is the live-trimmed P4 window in
the same convention. Par = corpus mean margin, 17.40 (sd 19.5, n = 240).

## Descriptive table (unchanged from v1; reproduced exactly by the reviewer)

| group | n | mean margin | vs par | mean dance transitions | mean stall turns |
|---|---|---|---|---|---|
| clean (no D-1, no stall) | 197 | 19.89 | +2.50 | 0 | 0 |
| dance only (D-1, no stall) | 16 | 7.81 | −9.58 | 14.1 | 0 |
| stall only (P4, no D-1) | 8 | 12.38 | −5.02 | 0 | 126.0 |
| dance + stall | 19 | 1.68 | −15.71 | 169.8 | 173.4 |

## Primary inference (map-blocked, exact)

- **Stall vs no-stall, discordant map pairs: n = 17, mean pair delta −24.29,
  exact one-sided p = 0.0000153.** The stall ASSOCIATION survives blocking and is
  stronger than v1's naive estimate.
- **Dance-only vs clean, discordant map pairs: n = 14, mean pair delta −7.07,
  exact one-sided p = 0.134.** NOT established. v1's "dance is a marker, not a
  mechanism" claim is therefore WITHDRAWN as a finding and downgraded to a
  hypothesis — consistent with T-1's graded 1/25 and the ≈ +0.045 pre-registration,
  but not demonstrated by this panel (n = 14 discordant pairs is also underpowered).
  v1's supporting assertion "fourteen dancing turns cannot mechanically cost twelve
  points" is withdrawn: it carried no opportunity-cost bound.

## Reading, revised

1. **Low margins are strongly ASSOCIATED with the whole-bot no-progress stall**
   (P4 liveness: ≥60 live turns without own-inventory/cargo progress while work
   remains). Association, not causation: the stall could depress the margin (idle
   workforce), or a lost position could produce both. Direction is NOT resolved by
   this analysis.
2. **Bring-to-par SCENARIO (not a ceiling, not a causal estimate):** if the 27
   stall-carrying games scored at par, the corpus mean would rise ≈ 1.41 points.
   This number is quotable ONLY with both conditions attached: (a) causality
   unresolved here; (b) fixability unresolved everywhere so far — see below.
3. **The fixability condition has a named discharge path, not an instrument:**
   claude_1 has flagged (2026-08-17 ack) that the pool-#3 cause table cannot say
   whether a stalled game was still winnable — a case can be assignment-failure
   labelled AND already lost. Per the adjudication template, step L1 (judge the
   game state first) at the OWNER SESSION is where that condition is discharged,
   case by case on the stall population, using the viewer. No new instrument is
   chartered for it.

## What this feeds at the verdict session (#6)

The frozen verdict rule asks whether parked-idle "explains" the margin deficit. This
analysis establishes: the deficit concentrates in stall-carrying games (blocked
p ≈ 1.5e-5), the dance-only deficit is not established (p = 0.134), the recoverable
amount IF stalls are causal AND fixable is ≈ 1.41 corpus points, and both IFs are
the session's to resolve (cause table for the first, L1 judgment for the second).

## Limits

Association-only; 27/16/8 strata named small; one corpus (c5), one subject (the
resident); panel-internal margin units; two pre-named contrasts; the dance+stall
group's windows coincide by construction, so no within-group attribution is made.
No cause label is asserted; the evidence gate holds.
