# Curriculum Level 1 teacher-auxiliary confirmation result — 2026-07-19

## Verdict

**Pass.**  The coefficient-0.10 online teacher auxiliary reproduces on an independent model seed,
behavior-cloning stream, PPO stream, and exact untouched 1,000-seed evaluation bank.  Level 1 is
accepted and randomized-worker Level 2 is authorized.

This result validates the learning mechanism only.  It does not change the resident and does not
authorize an Arena submission.

## Frozen confirmation result

The seed-53 behavior clone first passed its consumed-debug sanity gate at 93.6% overall, 92.77%
nonzero-deficit success, 91.16% height floor, median turn 38, and zero paired teacher delay.  The
fresh teacher and random-legal controls were then generated and hashed before learned evaluation.

On exactly seeds 2,002,000--2,002,999:

| Gate | Required | Observed | Result |
|---|---:|---:|---|
| Stage A overall success | >=70% | 93.4% | pass |
| Stage A nonzero-deficit success | >=65% | 92.49% | pass |
| Stage A height floor | >=55% | 90.04% | pass |
| Final overall success | >=85% | 99.7% | pass |
| Final nonzero-deficit success | >=80% | 99.66% | pass |
| Final height floor | >=75% | 99.60% | pass |
| Final paired teacher median delay | <=15 turns | 0 turns | pass |
| HARVEST / legal HARVEST | >=60% | 4,153 / 5,405 = 76.84% | pass |
| `MOVE current` waits | <=20,000 | 1,983 | pass |

The final policy solves 997/1,000 maps at median turn 42.  The exact teacher solves 1,000/1,000 at
the same median; random legal solves 119/1,000.  Final training throughput was 679.5
transitions/second over 1,000,000 transitions, with 68.66% aggregate host CPU and 1,471.62 seconds
wall time.

## Replication conclusion at several levels

- **Action:** deterministic deployment retains the required work ordering instead of collapsing
  to wait-like MOVE actions.
- **Trajectory:** two independent teacher-auxiliary runs exceed 99% exact-bank success, while the
  paired pure-PPO replicate fell to 18.2% at Stage A.
- **Optimization:** online teacher cross-entropy is a necessary stability constraint for the
  current PPO schedule, not a cosmetic boost.
- **Architecture:** BFS distance planes, behavior-clone initialization, and online teacher
  anchoring form the accepted minimum curriculum learner.
- **Scope:** the accepted task still controls one automatically selected troll completing one
  fixed recipe against a waiting opponent.  It says nothing yet about choosing worker specs,
  coordinating workers, renewable production, or adversarial transfer.

## Frozen artifacts

- protocol: `3dc06855d5d9e13ccf04ddf25176ffa42b3e31b8286f50101bff0f1df9ecff54`;
- behavior clone: `41bacadb4eb02f8af068140750994816ffd88f485c9d0e3fa35c7efda7fb6952`;
- Stage A checkpoint: `da82007546d5bbb917278ea3d31d6ca9e4cd62dcc350c71890251099415d842e`;
- Stage A evaluation: `7d3ca4a6726754c3e3194fa543ed10464e0653a036cd20bdd7f77654af9d0841`;
- final checkpoint: `344526f9deaa6743e6bec93d9fdf147d3dc3fd65005a3299a75fe62ac2ee965b`;
- final evaluation: `be06a158cf0051cf660fcdfa3e267b960dccbe23ac04d38d52dbc43ec2e5d211`;
- exact action audit: `802c744fb764d0854dc6e86d6d886c45255573fbf959f88d99b0fdd5de84e2f9`;
- training summary: `3f346fd1c0e797d6dbcd94bce0ee5dfda37dcc348b5c1e277bead09893b3c0c6`.

## Next experiment

Freeze Level 2 before generating labels: sample valid requested worker recipes rather than the
single `(1,3,0,1)` recipe, expose the requested capabilities in the observation, retain automatic
worker selection and the same action grammar, and require success by recipe family on an exact
held-out bank.  Build and verify the teacher/random controls before training.  Multiple-worker
coordination, learned recipe selection, opponents, and terminal score remain later levels.
