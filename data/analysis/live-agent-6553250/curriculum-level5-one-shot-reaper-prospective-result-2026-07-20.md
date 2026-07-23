# Curriculum Level 5 one-shot crop reaper prospective result — 2026-07-20

## Verdict

**Accept D4 without learning.**  On the frozen, previously unopened exact interval
2,023,000--2,024,999, the lifecycle-corrected teacher solves 1,999/2,000 = 99.95%, random legal
solves 0/2,000, and the unchanged accepted Level-4 actor solves 1,958/2,000 = 97.90%.  Every frozen
control, functional, stratified, interaction, and paired-timing gate passes.  No clone, PPO
transition, checkpoint selection, source deployment, or Arena action occurred.

## Frozen prospective controls

| Measure | Teacher | Requirement | Verdict |
|---|---:|---:|---|
| Overall / nontrivial success | **99.95% / 99.91%** | >=99% / >=99% | pass |
| Worst recipe / height | **99.61% / 99.80%** | >=98% / >=98% | pass |
| Player crop / renewable harvest | **99.95% / 99.95%** | >=99% / >=99% | pass |
| Illegal teacher selections | **0** | 0 | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent crop creation | **84.65%** | >=75% | pass |
| Opponent own-crop harvest | **50.40%** | >=45% | pass |
| Confirmed player-crop destruction | **78.50%** | >=70% | pass |
| Opponent above one worker / destruction above one | **0 / 0** | 0 / 0 | pass |
| Random-legal overall | **0/2,000** | <=5% | pass |

The teacher completes at median turn 61.  The opponent averages 29.543 score, creates 0.855 crops,
records 3.479 renewable harvests, and destroys 0.785 player crops per episode.  This independently
confirms that the deterministic D4 opponent is both economically active and materially disruptive.

## Unchanged Level-4 actor

| Measure | Result | Requirement | Verdict |
|---|---:|---:|---|
| Overall success | **1,958/2,000 = 97.90%** | >=95% | pass |
| Nontrivial success | **98.14%** | >=93% | pass |
| Worst recipe | **96.12%** | >=90% | pass |
| Worst height | **97.21%** | >=93% | pass |
| Player crop / renewable harvest | **98.20% / 99.40%** | >=97% / >=97% | pass |
| Paired-teacher median delay | **0 turns** | <=10 | pass |
| Positive opponent score | **100%** | >=95% | pass |
| Opponent crop / own-crop harvest | **78.90% / 51.15%** | >=75% / >=45% | pass |
| Confirmed player-crop destruction | **83.85%** | >=70% | pass |
| Opponent above one worker / destruction above one | **0 / 0** | 0 / 0 | pass |

The actor completes at median turn 64.5.  Its development and prospective success rates are
97.60% and 97.90%, respectively, so the result does not depend on an unusually favorable 500-seed
development block.  Of 42 prospective failures, 35 experience a confirmed destruction; only six
finish with a replacement crop and 30 had already completed a renewable harvest.  Conversely,
1,642 of the 1,677 destruction episodes still succeed.

## Analysis at different abstraction levels

### Mechanism

A rival can plant renewably and remove one player crop while retaining positive production, yet
the accepted controller still solves 97.90% of exact unseen tasks.  Destruction raises tail risk,
but one bounded loss is recoverable and cannot explain the rejected complete opponent's roughly
52% zero-shot result.

### Curriculum

D1 natural contention, D3 opponent planting/self-renewal, and D4 one-shot crop destruction all
transfer prospectively without policy adaptation when the opponent remains at one worker.  The
largest unisolated discontinuity in D0 is now natural workforce growth and the resource/scheduling
parallelism it creates.

### Learning

The actor remains 2.05 percentage points below the prospective teacher, but exceeds all fixed
functional and stratified floors with zero median paired delay.  Spending labels on D4 would fit a
narrow failure tail rather than address the next causal gap.  The accepted checkpoint therefore
remains byte-identical.

### Goal and transfer

This is an abstraction acceptance, not an Arena candidate.  The task still supplies a requested
recipe and does not perform autonomous opening or macro-strategy selection.  D4 provides no direct
evidence that the resident source improves against live strategic opponents and authorizes no
submission.

## Next experiment

Freeze a D5 development protocol that adds exactly one **naturally funded** opponent worker and
caps the opponent at two.  Keep the accepted one-worker interaction stack and player task fixed;
measure whether the second worker is actually trained, remains productive, and changes task
success.  This tests workforce/resource compounding without reopening the complete baseline's
unbounded training and broad policy bundle.

## Reproducibility anchors

- prospective protocol:
  `eb5f9d5ab0d6fdbffa796d0488bfaab10fb8721ab1c5c0749f7e80dbe301e07a`;
- teacher artifact:
  `85375f4db38dcff5e851ff27f901a4d9119d4e2aabd52df9dc0a9a2ba437827c`;
- random-legal artifact:
  `cab68cd47b876a4126ad7cf64ec2dbbca471ad6de896418f6439025e750b71a1`;
- fixed-actor artifact:
  `9ec71b30e03a9e20b2c789321cd5d4fe0a7c26e0bf3a2b94699c6c4237fdecef`;
- accepted Level-4 checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
- Rust environment source:
  `bc3f6e3caa2ffe49b3e26a7c35bf08559c7ecf6c01a69c6e9a08cc615993601d`; and
- Python Level-5 wrapper:
  `4755d98bbcca527f96dc153824320532d62e3cc699e763a7d1bb3031432818be`.
