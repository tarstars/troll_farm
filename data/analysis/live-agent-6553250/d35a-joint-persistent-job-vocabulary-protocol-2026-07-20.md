# D35a joint persistent-job vocabulary audit — protocol (2026-07-20)

## Purpose

D34 selected a coherent joint production/suppression scheduler as the next representation.  D35a
tests the prerequisite question before implementing an executor or training a policy: can a small,
persistent job vocabulary actually explain the complete multi-worker schedules observed in the
frozen rich field cohort?

This is an observational representation audit on already-consumed replays.  It cannot select a
candidate, estimate causal value, fit a policy, open a fresh seed, invoke TestSession, or authorize
Arena activity.

## Frozen cohort and split

- Exact 21 `rich3plus:farm_wood:train_now` opponent trajectories from
  `rich-opponent-scheduler-transition-2026-07-19.json`.
- Preserve the old outcome-blind partition: 12 discovery games and nine confirmation games.
- Re-fetching a game is permitted only to reconstruct its exact per-turn state and command stream;
  cohort membership, partition, player seat, and every gate are frozen before those streams are
  decoded.
- Require exact decoded/command turn counts, zero unknown replay-diff updates, exact worker/TRAIN
  identity, and exact final signatures already established by the parent study.

## Frozen unit-job vocabulary

Every active unit-turn receives exactly one label:

1. `RENEW`: harvest, pick, plant, or fruit-bearing bank work;
2. `FELL_BANK`: chop and wood-bearing bank work on natural or own-attributed trees;
3. `PRESSURE`: chop work whose target is an opponent-attributed crop;
4. `MINE_BANK`: mine and iron-only bank work;
5. `MIXED_BANK`: a drop carrying materials from more than one economic family;
6. `IDLE`: explicit wait with no resolvable persistent job; or
7. `UNKNOWN`: a command that the frozen decoder cannot assign.

Initial plants are neutral.  A new plant is attributed to a side only from that side's exclusive
pre-step `PLANT` cell; simultaneous same-cell claims remain ambiguous.  A direct `CHOP` uses the
tree under the unit.  `DROP` uses the unit's pre-step cargo.  `HARVEST`, `PICK`, `PLANT`, and `MINE`
have direct semantic labels.

`MOVE` is not a job.  Search the same unit's next 12 active turns for the first direct non-MOVE,
non-WAIT job and inherit that label.  If none exists, inherit the immediately preceding non-idle
job only when the current explicit move target equals the previous move target; otherwise label it
`UNKNOWN`.  This is deterministic look-ahead decoding, not a deployable feature.

`TRAIN` is a global allocation flag.  The joint signature for a turn is the flag plus unit labels
ordered by stable worker ordinal.  Message commands are ignored.

## Measurements

For discovery and confirmation separately report:

- total and covered unit-turns;
- direct productive-command coverage;
- MOVE resolution within 12 active turns;
- label shares and worker-ordinal shares;
- run-length distribution of consecutive identical non-idle jobs;
- joint-signature count and coverage of the 8, 16, and 32 most common signatures;
- fraction of turns with at least two active workers and at least two distinct non-idle roles;
- `RENEW -> FELL_BANK`, `RENEW -> PRESSURE`, and funding-period role transitions; and
- successful plant provenance, ambiguous claims, and pressure-target counts.

Training periods are the intervals from the preceding successful TRAIN (or turn one) through the
next successful TRAIN.  They are descriptive contexts; they do not change job labels.

## Frozen representation gate

The vocabulary passes only if both discovery and confirmation satisfy all conditions:

1. replay integrity passes completely;
2. 100% of direct `HARVEST/PICK/PLANT/CHOP/DROP/MINE` commands receive a non-unknown label;
3. at least 95% of all active unit-turns receive a non-unknown label;
4. at least 90% of MOVE turns resolve to a persistent job;
5. median non-idle run length is at least three turns;
6. the 32 most common joint signatures cover at least 90% of turns;
7. `RENEW` and `FELL_BANK` each contribute at least 15% of covered non-idle unit-turns;
8. `PRESSURE` or `MINE_BANK` is observed in at least 1% of covered non-idle unit-turns; and
9. at least 25% of multi-worker turns contain two or more distinct non-idle roles.

These gates test compactness, persistence, productive breadth, and actual joint scheduling.  They
are not performance thresholds.

## Continuation rule

- **Pass:** freeze D35b: implement the exact job state, deterministic executors, assignment
  collision rules, and a closed-loop official-map teacher/oracle.  D35b must compare terminal own
  score and opponent score separately and preserve at least half of D34's productive-farm gain
  while reducing its opponent-score excess materially.
- **Fail:** do not build a macro PPO environment.  Inspect the specific uncovered command/job
  family and either expand the vocabulary once from source semantics or reject job-level control
  in favor of a recurrent primitive policy.  Thresholds and the 12-turn look-ahead are not tuned on
  the confirmation rows.

## Planned artifacts

- analyzer/fetcher: `cgauto/analyze_d35a_joint_job_vocabulary.py`;
- focused tests: `tests/test_analyze_d35a_joint_job_vocabulary.py`;
- machine result and written verdict in this directory.

