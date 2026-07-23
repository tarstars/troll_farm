# Opponent-crop Phase 21 arena verdict — 2026-07-19

## Decision

**Do not promote or resubmit the exact `b100_e6` candidate.  The exact resident has been
restored.**

The candidate was safe and showed the intended live mechanism, but it did not clear the frozen
rating rule before arena scheduling plateaued.  The protocol required an ambiguous 120-game result
to extend to 180 and then exceed the mature control by at least +0.5 on two final reads.  The
platform stopped at 160 games for more than 15 minutes, so the required read was unavailable.
Thresholds were not changed after observing the data; Step 9 closed the transfer as infrastructure
ambiguity.

## Frozen artifacts

| Role | Bytes | SHA-256 |
|---|---:|---|
| Resident/control | 62,725 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| Candidate | 64,522 | `6f992a5a4d58e5f3f78478322ab0f3ce6cf8706d5aa9bb57d10f8264b03a3f19` |

## Arena sequence

| Role/read | Agent | Submission | Games | Score | Rank | Catastrophic rate | Negative mass | Runtime signals |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Control 60 | 6560240 | 41012256 | 60 | 24.45 | 23 | 21.7% | 3,677 | 0 |
| Control 120+ | 6560240 | 41012256 | 122 | 24.83 | 18 | 17.2% | 6,113 | 0 |
| Control confirmation | 6560240 | 41012256 | 160 | 24.77 | 18 | 19.4% | 9,195 | 0 |
| Candidate 60+ | 6560269 | 41012399 | 61 | 24.45 | 22 | 18.0% | 2,149 | 0 |
| Candidate 120+ | 6560269 | 41012399 | 129 | 24.58 | 20 | 18.6% | 5,677 | 0 |
| Candidate plateau | 6560269 | 41012399 | 160 | 24.89 | 17 | 19.4% | 7,771 | 0 |

The 60 gate returned `continue`.  At 129 games, score delta was -0.25, catastrophic-rate gap was
+1.39 percentage points, and negative-mass ratio was 0.929; the frozen evaluator returned
`extend-180`.  At matched 160 games the candidate was only +0.12 in rating, with equal catastrophic
frequency but 15.5% less negative-margin mass.

## What transferred

Unpaired full-replay censuses show a coherent live mechanism:

- catastrophic crop interception: 22.7% control -> 33.7% candidate;
- our catastrophic-cohort wood from opponent crops: 13.3 -> 25.0;
- catastrophic mean margin: -238.8 -> -207.6;
- opponent crop wood: 84.0 -> 82.7 despite candidate opponents planting 7.4 more crops and using
  0.32 more workers on average.

This supports provenance-aware, baseline-preserving scheduling as a research direction.  It does
not satisfy the deployment or rank-3 objective.  The field censuses are unpaired and opponent/map
mix changed.

## Runtime audit correction

Two timeout strings belonged to opponents that scored -2.  The collector now attributes runtime
text by `$0`/`$1` player references rather than by the frame carrying stdout.  Both seat directions
have regression tests.  Re-audited candidate checkpoints contain zero candidate validity/runtime
signals.

## Restoration

The resident was explicitly restored as submission `41012593`, agent `6560289`.  Recovered saved
source is byte-exact at the resident SHA above.  The submit helper remains resident-defaulted.

## Consequence for the next cycle

Close this exact transfer and do not tune its bonus, ETA, or arena threshold on consumed games.
The next experiment should preserve the demonstrated value of provenance-aware residual scheduling
while seeking a larger effect, or attack complete worker-rich economy with a genuinely closed-loop
outcome-optimized controller.  It must not reopen isolated TRAIN wrappers, the current first-move
rollout library, or teacher-state imitation.
