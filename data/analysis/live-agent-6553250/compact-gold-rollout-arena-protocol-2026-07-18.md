# CompactGold rollout controlled arena protocol — frozen 2026-07-18

## Authorization and scope

The user authorized continuation after the locally qualified rollout candidate was explicitly
described as requiring a controlled arena trial.  This protocol authorizes only:

1. a fresh same-source capacity control using the current 62,725-byte resident;
2. the frozen 90,643-byte rollout candidate if and only if the control is healthy;
3. restoration of the resident source if the candidate does not clear the promotion gate.

Do not edit `cgauto/api_submit.py`, change either source, tune the selector, or submit another
candidate based on these results.

## Frozen sources

- Resident/control: `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, SHA-256
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`, 62,725 bytes.
- Candidate: `candidate-agent6553250-compact-gold-rollout30.min.rs`, SHA-256
  `f5df1f760791a21ad0193469c132fea02ebaa2856b33f62213765205b3b59370`, 90,643 bytes.

The resident was rank 23/104 Legend at 24.4 immediately before reset.  The capacity control was
submitted at 2026-07-18 09:31:01 MSK as submission `41009795`; its fresh agent is `6559490`.

## Capacity-control gate

Read the authoritative arena-room score and listed finished-game count around +5, +10, +20,
+35, and +50 minutes.  Ordinary early placement dips are not verdicts.

The control is healthy only if:

- games arrive continuously rather than in isolated waves;
- no compile or runtime failure appears;
- at least 120 finished games accrue by the formal comparison read;
- two mature reads at least five minutes apart differ by at most 0.5;
- the mature bracket is no more than 1.0 below the pre-reset 24.4 score.

If the control is unhealthy, do not submit the candidate.  Leave or restore the identical
resident source and record an inconclusive capacity result.

## Candidate gate

If control passes, submit the frozen candidate once.  Use the same read cadence, minimum 120
finished games, and two mature reads at least five minutes apart within 0.5.  Compare the mature
candidate bracket with the freshly measured control bracket, not with an older historical score.

- **Promote:** candidate bracket is at least control +1.0, with no timeout/runtime signal.
- **Neutral / insufficient:** candidate is between control -0.5 and control +1.0.  Restore the
  resident because the extra engine and first-turn compute have not demonstrated arena value.
- **Reject:** candidate is below control -0.5, has a compile/runtime failure, or shows any
  timeout signal.  Restore the resident immediately.

After restoration, confirm the current agent uses the resident source through the explicit
submission response and arena agent change.  Do not infer source identity from announcements,
which are intentionally identical.

## Interpretation

This is an unpaired rating transfer test under live matchmaking, not a causal paired estimate.
The same-code reset controls current capacity and rating drift; comparable sample sizes and
stable late reads reduce, but do not eliminate, opponent-mix noise.
