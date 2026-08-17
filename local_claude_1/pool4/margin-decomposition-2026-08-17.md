# Pool #4 — margin decomposition: what actually travels with the low margins

Integrator deliverable (`local_claude_1`), 2026-08-17. Method-verification owed by
codex_1 per the iteration charter. Recomputed entirely from the committed
`claude_1/t1/t1-matched-floor.json` (the resident's own 240-game replay); script:
`local_claude_1/pool4/decompose.py` (deterministic, seed pinned).

**Unit caveat, first:** "margin" is the panel's internal per-game score margin
against a frozen opponent stream — NOT arena rating points. Valid for within-corpus
comparison only. "Par" = the corpus mean margin, 17.40 (sd 19.5, n = 240).

## The table

| group | n | mean margin | vs par | mean dance turns | mean stall turns |
|---|---|---|---|---|---|
| clean (no D-1, no stall) | 197 | 19.89 | **+2.50** | 0 | 0 |
| dance only (D-1, no stall) | 16 | 7.81 | **−9.58** | 14.1 | 0 |
| stall only (P4, no D-1) | 8 | 12.38 | −5.02 | 0 | 126.0 |
| dance + stall | 19 | 1.68 | **−15.71** | 169.8 | 173.4 |

("stall" = the P4 liveness violation: no own-inventory/own-cargo progress across a
≥60-live-turn window while work remains. "dance turns" = summed D-1 episode windows.)

- All D-1 games together: −12.91 vs par — reproducing the known "≈13.6 below par"
  figure on this corpus.
- Stall games (any): −12.54 vs par, one-sided permutation p ≈ 0.0001.
- **Dance-WITHOUT-stall games: −12.08 vs clean (p ≈ 0.006) with only ~14 turns of
  dancing on average.** Fourteen turns of pacing cannot mechanically cost twelve
  points — T-1's graded result already priced the dance at ≈ nothing.

## Reading, stated carefully

1. **The catastrophic bucket is dance + stall** (19 games, 8% of the corpus,
   −15.7 each): whole-game windows where a troll dances AND the bot as a whole makes
   no progress for ~170 live turns while work remains. This is the population the
   standing-troll audit is anatomizing. If — causality pending pools #3/#5 — these
   games were brought to par, the corpus mean would rise ≈ 1.24 points; adding the
   stall-only bucket brings the ceiling to ≈ 1.41. Material against a ≈ 2-point goal
   gap, IF the causal story holds.
2. **The dance itself is a MARKER, not a mechanism.** Short-dance games with no
   stall still run ~10–12 points below their peers. Something about those game
   states is hard, and it both depresses margins and produces brief dances; curing
   the dance there would cure the symptom of a symptom. This is fully consistent
   with T-1's measured 1/25 and its ≈ +0.045 price.
3. **What this does NOT establish:** causality in either direction. Correlations are
   modest (margin vs stall −0.25; vs dance −0.26; the dance+stall group is
   collinear by construction — the windows coincide). The stall could depress the
   margin (idle workforce), or a lost-position game could produce both. The cause
   table (#3) and mechanism notes (#5) carry the causal burden; this analysis
   carries the PRICE CEILING and the marker-vs-mechanism separation.

## What this feeds at the verdict session (#6)

- The frozen verdict rule asks whether "parked-idle explains the margin deficit."
  Refined by this data: the deficit concentrates where the whole bot stalls while
  work remains — the stall is the billable event; the dance is mostly a marker.
- Benign-branch evidence: 16 of 35 dance games have NO stall — for those, "ignore
  the dance" already looks right.
- Illness-branch evidence: 27 games carry stalls worth ≈ −1.4 corpus points ceiling
  — the cure question is whether pools #3/#5 show those stalls to be assignment
  failures (fixable) or lost-position consequences (not billable).

## Limits

Small strata (8 and 16); panel-internal margin units; live-trimmed stall windows
per the P4 rule; one corpus (c5), one subject (the resident); no multiple-testing
correction beyond the two pre-named contrasts; nothing here asserts any cause
label — the evidence gate holds.
