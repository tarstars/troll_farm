# E2 banking-route efficiency — result

Date: 2026-07-30  
Verdict: **`ROUTE_RESIDUAL_OBSERVED — NOT_EXPERIMENT_JUSTIFIED`**

## Decision

The exact live resident does not waste carrying time through a longer immediate home-door
route, a suboptimal two-carrier door assignment, or a changing door target. A small,
strictly hindsight residual remains: in 134 completed wood returns, an inbound-ETA-tied
alternate door would have been one turn nearer the productive target observed only after
deposit. That is 134 avoidable movement turns over 400 side-games, or 0.335 per side-game,
with a maximum of one per episode.

This is a real descriptive tie-break residual, so `NO_ROUTE_RESIDUAL` would be false. It is
not an experiment lead: the next task is future-conditioned, the calculation is static and
non-causal, and M1 provides no valid movement/margin-to-rating conversion. No policy,
candidate, fresh range, or Arena action follows.

## Scope and non-duplication

The 2026-07-16 motion audit established zero no-progress, duplicate-landing,
stationary-teammate-target, or door-stall events across 34,427 moves. D171/D176 separately
diagnosed and treated repeated non-bank target reversals. Neither asked which reachable home
door a carrier selects or whether that door is favorable for its later outbound task.

E2 therefore froze three distinct quantities:

1. immediate inbound ETA regret, holding the other selected unit target fixed;
2. joint assignment regret when both resident units return simultaneously;
3. target changes before deposit and static hindsight return-plus-next-leg regret.

## Method

- Source: exact live
  `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`,
  62,725 bytes, SHA-256
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
- Panel: reused deterministic Bronze seeds `0..199`, both seats, exact live source versus
  itself. This opens no fresh, sealed, or confirmation range.
- A provisional return begins only when a unit carrying positive cargo emits `MOVE` to a
  walkable home-door cell, or emits `DROP` while on one. A moving episode is confirmed as
  banking only by a later positive-cargo `DROP` at a home door without intervening cargo
  change; interrupted or terminally censored episodes remain unidentified.
- Immediate eligibility reproduces reachable doors, resident occupied-door filtering, the
  other selected action's semantic target, BFS distance, and `ceil(distance/speed)`.
  Simultaneous carrier assignments are enumerated jointly with distinct target cells.
- After deposit, the observer binds the first non-wait productive target. The hindsight
  ceiling compares static
  `start → deposit door → observed next target` against the best reachable home door.
  This conditions on a future target and does not replay the counterfactual policy.

## Integrity

- 200/200 seed rows and 400/400 seat rows are present; 192 games end by stall, median
  terminal turn 168.
- Seven focused tests and the built-in self-test pass.
- A 16-seed jobs-1/jobs-8 rerun is byte-identical:
  `78a16561567cf7bcce41f1b7f4a029188ddfed6ab7691775aa5e9c1615335d7b`.
- Compact JSON recomputes exactly from the detailed rows; seed and seat coverage, detail
  hash, and byte count validate.
- Analyzer SHA-256:
  `d3649bd45c201873a9302d40670e8a7434a73a7805e9198c0cd98c7d8995e835`;
  tests:
  `bcc1632ee5b5bec1bac3ec095cf2935ae279b165615590d58d7612ee5bc407ea`.
- The byte-sacred development resident remains
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Coverage

- 11,267 provisional episodes.
- 11,260 confirmed deposits in all 400 side-games, carrying 14,695 cargo units.
- Seven returns end with the game before deposit and remain unidentified.
- 10,597 deposits bind a later productive target; 663 end before one appears.
- 4,873 confirmed carrying door-move checks, of which 4,855 are immediately identifiable;
  the 18 resident-specific forced/occupied-door cases are retained but not scored.
- 64 simultaneous two-carrier assignment checks, all identifiable.

## Findings

### Immediate return is already optimal

All 4,855 identifiable immediate checks have zero ETA regret. All 64 joint checks have zero
assignment regret. No confirmed return changes its door target. Thus the resident's
immediate BFS/ETA rule and two-worker exhaustive pairing do what they claim; the prior
motion audit's clean execution was not hiding route drift.

### The only residual is post-deposit hindsight

Of 10,597 next-target-bound deposits, 134 (1.2645%) admit a one-turn lower static
return-plus-next-leg ETA through another home door. They occur in 105/400 side-games:

- total avoidable movement turns: 134, or 0.335 per side-game;
- maximum per episode: one turn;
- total static cell difference: 716;
- cargo: 134/134 wood-only;
- movement speed: 120 at speed 2, 14 at speed 3;
- seat balance: 67/67.

Every positive episode uses one immediate-optimal inbound move and has no target change.
The apparent loss exists only after conditioning on what the scheduler later chooses:
109 next targets begin with `MOVE`, 24 with `CHOP`, and one with `PICK`.

## Interpretation and boundary

E2 closes immediate banking-route correction and persistent-door routing as candidate
classes. A future-aware tie-break could theoretically select among equal inbound-ETA doors,
but this audit supplies only a 0.335-turn-per-side-game static ceiling, not terminal value.
It therefore does not clear the register's ≥+1.0 rating evidence bar and must not be
materialized as a policy experiment from these data.

This boundary does not close E4's broader question about incidental BFS/candidate tie-breaks
outside banking. It does require any E2 successor to produce a causal terminal-value bound
before source work, and it forbids presenting these 134 hindsight turns as score or rating.

## Artifacts

- Compact machine result:
  `data/analysis/live-agent-6553250/e2-banking-route-efficiency-result-2026-07-30.json`,
  SHA-256
  `3280f8306e7f73cc679e997e54e853fb935a5f78375eeb9b1c6b3e8fa1238064`.
- External-backed episode detail:
  `outputs/local_codex_1/e2-banking-route-efficiency/e2-episode-details-0-199.json`,
  14,794,834 bytes, SHA-256
  `54aa05584a3f77b15c8c133bede7d85e05d58d668081dfa3b1f72a76ebbc0fd1`.
- Analyzer: `cgauto/e2_banking_route_audit.py`.
- Tests: `tests/test_e2_banking_route_audit.py`.

