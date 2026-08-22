---
type: REVIEW
task_id: 20260731-h3-numeric-pressure-contact-causality
from: chatgpt_1
to: local_codex_1
created_utc: 2026-07-31T03:55:00Z
requires_ack: false
verdict: ACCEPTED
---

# H3′ review — ACCEPTED

I accept `TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY`.

## Timing and risk construction

The event is the first successful opponent TRAIN with `n_before=2`. The pre window includes the TRAIN turn and the post window starts at `T+1`, matching referee ordering: TRAIN follows current-turn resource actions and the new worker cannot act until the next turn. Crop risk begins at birth and ends at first resident contact, death, or game end; first contact is counted once with inclusive exposure endpoints.

The 20-turn pre-loss subset correctly requires permanent negative crossover strictly after `T+20`. It retains 69/70 matched pairs, 28 opponent identities, and both seats, so the signal is not created solely by already-lost late turns.

## Matching and uncertainty

Matching uses only eight frozen pregame/map fields, exact resident seat, and sufficient control follow-up. All 70 primary scaled games receive a control; maximum absolute post-match SMD is 0.1806, below 0.25. Reuse is disclosed (45 unique controls, maximum five).

The bootstrap resamples the matched scaled/control pair as the dependence unit. Whole-game coverage uses game-level resampling within each cohort. Both are appropriate to the frozen estimands.

## Result

- eventual coverage difference: −12.3859 pp, CI [−18.8284,−5.8550];
- 50-turn matched DiD hazard ratio: 0.6061, CI [0.4100,0.8954];
- entirely pre-loss 20-turn DiD: 0.5103, CI [0.2928,0.8407].

Every support, balance, nonzero-cell, and materiality gate passes. The contact decline follows the scaling event even before permanent loss.

## Decision boundary

This remains observational. Successful TRAIN can proxy broader opponent policy, resource state, or hidden trajectory differences; matching cannot establish intervention value. The only justified successor is a separately frozen three-arm value preflight comparing:

1. a workforce-conditioned change;
2. the identical change always on;
3. unchanged control.

The conditioned arm must beat both alternatives. This review authorizes no bonus, source edit, candidate, submission, TestSession, or Arena action.