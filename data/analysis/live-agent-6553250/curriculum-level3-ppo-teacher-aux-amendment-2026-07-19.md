# Curriculum Level 3 PPO teacher-auxiliary amendment — 2026-07-19

## Invalidated launch

The first official process on training stream 6,100,000 is invalid and stopped before Stage A.  It
reached 330,000 decisions and never evaluated a learned policy on the prospective bank.  Beginning
at update 26, masked teacher cross-entropy alternated between approximately `3.4028234e35` and
`Infinity`.  Continued high rollout success does not rescue a non-finite loss contract, so the
process carries no discovery evidence and its stream is consumed.

Invalid trainer source hash:
`b22b059b5d19185fb4d16916ce941840ecb2687a45c68bb35b8d5e486ef0edb2`.

## Root cause

The deterministic teacher is guaranteed legal on its own trajectories, but PPO queries it on
learner trajectories.  A fixed-seed random-trajectory diagnostic checked 500,000 such labels and
found 2 illegal commands (0.0004%).  Both were farmer `PLANT_BANANA` commands at the designated
cell after the learner had already placed a PLUM there while carrying BANANA.  The teacher's
preferred action was therefore undefined in that off-teacher state.

The actor mask represents an illegal logit with negative float maximum.  Passing that location as
the cross-entropy target creates the observed huge/non-finite loss even though the event is rare.
The failure is in auxiliary-label handling, not the referee, reward, observation, action mask,
teacher baseline, or renewable objective.

## Minimal repair

For each minibatch, teacher auxiliary cross-entropy and teacher accuracy are computed only over
rows where the teacher command is legal in the stored action mask.  Undefined off-teacher rows
receive no supervised loss.  PPO policy/value loss, reward, entropy, legal action sampling, all
valid teacher labels, the coefficient 0.10, model, and every gate remain unchanged.

Each update now records `teacher_invalid_labels` and `teacher_legal_rate`; the final summary records
their exact aggregate.  A unit test injects an illegal teacher target and verifies finite loss on
the remaining legal row.  The focused learner/environment suite passes 13/13, and a fresh
development-only end-to-end smoke completes both Level-3 evaluation paths with finite losses.

Corrected trainer source hash:
`e55a8cf1f1ff3b9bc77b8f24769d35cb89b3098e630574cbb4ab47abb83b4351`.

## Revised prospective launch

The exact teacher/random controls and seeds 2,011,000--2,012,999 remain prospective because the
invalid process stopped before its first learned evaluation.  The replacement run uses fresh
training stream 6,200,000 and run name `renewable-run1b-ppo`; it restarts from the unchanged clone
checkpoint and model seed 71.  Every other command argument and every frozen functional/action
threshold is identical to the launch record.

This amendment is frozen before replacement training.  A Stage-A failure still stops, and a final
functional pass still requires the independent strict action audit and confirmation.
