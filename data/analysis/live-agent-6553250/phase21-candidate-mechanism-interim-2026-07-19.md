# Phase 21 candidate mechanism interim — 160 games, 2026-07-19

## Status

The `b100_e6` candidate has reached the platform's apparent 160-game scheduling plateau.  The
frozen protocol requires 180 games and +0.5 over the mature control on two final reads, so there is
**no deployment verdict yet**.  This report preserves mechanism evidence while waiting; it does
not alter the arena gate.

Both full replay censuses parsed without fetch failures:

- exact-resident control: 131 games, agent `6560240`;
- candidate: 160 games, agent `6560269`.

The sets are unpaired and have different opponent/map mixtures.  Differences below are descriptive
field transfer evidence, not causal treatment estimates.

## Matched-count arena checkpoint

At 160 listed games each:

| Measure | Control | Candidate | Difference / ratio |
|---|---:|---:|---:|
| Arena score | 24.77 | 24.89 | +0.12 |
| Rank | 18/107 | 17/107 | +1 place |
| Wins / ties / losses | 82 / 2 / 76 | 84 / 6 / 70 | descriptive |
| Mean final margin | -20.70 | -12.53 | +8.18 |
| Catastrophic losses | 31 (19.4%) | 31 (19.4%) | equal |
| Total negative-margin mass | 9,195 | 7,771 | -1,424 (-15.5%) |
| Candidate runtime/validity signals | — | 0 | clean |

The equal catastrophic count but smaller negative mass is directionally consistent with reducing
tail severity.  The +0.12 rating difference is below the protocol's extended +0.5 promotion bar.

## Mechanism transfer

| Catastrophic-cohort measure | Control census | Candidate census | Difference |
|---|---:|---:|---:|
| Games | 25/131 (19.1%) | 31/160 (19.4%) | different unpaired samples |
| Mean margin | -238.76 | -207.65 | +31.11 |
| Opponent-created crops | 42.56 | 49.94 | +7.38 |
| Our crop interception rate | 22.69% | 33.69% | +11.01 pp |
| Our wood from opponent crops | 13.32 | 25.03 | +11.71 |
| Opponent wood from own crops | 84.04 | 82.68 | -1.36 |
| Opponent workers | 3.36 | 3.68 | +0.32 |
| Opponent final score | 446.24 | 426.61 | -19.63 |

The candidate cohort faces more opponent crops and more workers, yet contacts substantially more
of those crops, takes nearly twice as much wood from them, and holds opponent crop wood roughly
flat.  This is the exact behavioral direction intended by provenance tracking plus the bounded
priority bonus.  Across all games, interception rises more modestly from 49.95% to 51.48%, which
fits a treatment concentrated in the dangerous tail rather than a global policy replacement.

## Runtime-attribution audit

Two apparent timeout strings were opponent failures in games `896285678` and `896286624`:

- the candidate won 114 to -2 and 260 to -2;
- target agent records were `valid=true`;
- raw summaries/tooltips attributed the failures to `$1` and `$0` respectively, both the opponent
  seat in their game.

The checkpoint collector now extracts only player-addressed summary lines and tooltips for the
target seat.  Reversed-seat regression tests cover both cases.  The corrected 160-game candidate
audit has zero runtime/validity signals.

## Interpretation at several levels

1. **Implementation:** provenance tracking activates on official games in the intended direction.
2. **Mechanism:** crop interception and tail severity improve descriptively; the candidate does not
   eliminate worker-rich opponent compounding.
3. **Policy:** a small scheduling nudge transfers more faithfully than prior complete-policy
   replacements, supporting baseline-preserving residual interventions as an architecture.
4. **Statistics:** the arena score advantage is only +0.12 at matched count and the censuses are
   unpaired.  Mechanism evidence cannot be promoted into a rating claim.
5. **Goal:** rank 17 is far from the standing rank-3 objective even if this candidate eventually
   passes.  A promotion would establish a better baseline, not finish the project.

## Next decisions

- Keep the candidate active while waiting for the 180-game protocol read; do not change its source
  or thresholds.
- If it reaches 180 at score at least 25.27 with clean safety metrics, start the required delayed
  final confirmation.
- If it is below the extended bar, or the 180 read remains unavailable because the platform has
  capped scheduling, restore the exact resident under the frozen rejection/ambiguity rule.
- Carry the observed value of provenance-aware scheduling into hypothesis generation, but do not
  retune this exact treatment on consumed arena games.

## Evidence

- `phase21-candidate-field-census-2026-07-19.json`;
- `phase21-control-field-census-2026-07-18.json`;
- `opponent-crop-phase21-candidate-160-interim.json`;
- `opponent-crop-phase21-control-confirm.json`.
