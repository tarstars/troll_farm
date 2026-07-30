# M1 rating-system dynamics — result

Verdict: **DESCRIPTIVE_ONLY** (support: **PARTIAL**).

## Source and panel

- Source integrity: PASS; 8,014 raw games decoded and 2,564,403,129 bytes hash-verified.
- Raw coverage limits: 105 recorded fetch failures and 1,931 battle IDs without an admitted raw result; bracket completeness excludes them.
- Leaderboards: 7 collections, 6 unique responses, 2549 score-changing exact-agent intervals; all 2549 coincide with advancing `updateTime`.
- Battle lists: 243 observations for 55 agents; lengths 101–274 (median 137).
- Score-field convention resolved: True; leaderboard alignment 97.1%.

## Identification

- Internal score transitions: 329; outcome-complete: 307 across 45 agents (93.3%).
- Complete exposure contains 2147 wins, 2511 losses, and 0 ties.
- Source FULL-eligible before fitting: True; PARTIAL-eligible: True.

## Candidate-rule validation

| model | held-agent MAE | median AE | zero baseline |
|---|---:|---:|---:|
| affine | 0.479389 | 0.307776 | 0.478583 |
| net_wins | 0.481121 | 0.289683 | 0.478583 |
| elo_like | 0.477313 | 0.284044 | 0.478583 |

The best prior-epoch model improves on predicting zero change by only 0.27%; its MAE is 0.477313, far above the 0.05 recovery gate.

Selected descriptive model: `elo_like`. No wins-per-+1 estimate is reported unless the rule is RECOVERED.

## Convention and sensitivity checks

- Alternative next-epoch convention: 307 complete transitions; best model `elo_like`; all recovery gates do not pass.
- Excluding the first July 21 snapshot: 282 complete transitions across 45 agents; best model `elo_like`; recovery gates still fail.
- Resident: 5 observed score epochs and 3 complete transitions.

## Decision consequence

The stored panel does not earn a causal wins-per-score conversion. Preserve the exact membership and documented pre/post score for each platform recomputation, or obtain the platform formula: this panel already has broad transition coverage, but wins/losses and the tested Elo-like residual do not predict held-agent score changes.

This was read-only. The resident and Arena were untouched.
