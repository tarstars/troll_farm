# Curriculum Level 1 online teacher-auxiliary protocol — frozen 2026-07-19

## Hypothesis

The pure-PPO replicate fails because entropy and policy-gradient updates move the deterministic
argmax from HARVEST to `MOVE current`, even though stochastic rollouts retain successful actions.
An online teacher cross-entropy term on the same rollout states should prevent that mode collapse
without removing PPO return learning.

This is the one auxiliary-loss test authorized by the BFS/BC protocol.  It is a paired mechanism
test on consumed data, not a fresh confirmation and not a submission gate.

## Frozen comparison

Everything matches failed pure-PPO replicate run two except the auxiliary term:

- initial checkpoint SHA-256:
  `4c6365f7c1f5ce0836c9583ccc2d55df934606c0d75f27b6a1b31ac693655f21`;
- model seed 47;
- PPO training seed base 3,100,000;
- exact consumed evaluation bank 2,001,000--2,001,999;
- 100 environments x 100 rollout steps, 250k Stage A, one million maximum;
- four epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value 0.5, reward scale
  0.01, gradient norm 0.5, target KL 0.03;
- online teacher auxiliary coefficient: constant 0.10;
- teacher labels are generated from each rollout state before the selected action is stepped;
- no offline corpus, replay, new teacher states, or fresh evaluation seeds.

The implementation logs minibatch teacher loss and deterministic teacher-action accuracy.  The
training script SHA-256 at freeze is
`27b60ec65197c9e3f59fe8a92842220e9ec2aa7e0bcdd4cc544a83888d095613`.

## Gates

At 250k, use the original BC Stage A thresholds on the consumed exact bank: at least 70% overall,
65% nonzero-deficit, 55% height floor, and teacher median +25 turns or better.  Failure stops and
closes coefficient tuning.  Passing continues the unchanged schedule to one million transitions.

At one million, require the original final thresholds: 85% overall, 80% nonzero-deficit, 75%
height floor, and teacher median +15 turns or better.  A post-run exact action audit must also show
at least 60% HARVEST selection on legal HARVEST opportunities and no more than 20,000
`MOVE current` waits across 1,000 episodes.

## Decision rule

- Failure closes this auxiliary formulation; do not tune the coefficient on the consumed bank.
- Passing proves the collapse mechanism is controllable but remains development evidence only.
- After a pass, freeze one new exact confirmation bank and a fresh model/training seed before
  claiming reproducibility or opening Level 2.
- The resident source, Arena agent, and submission remain unchanged throughout.

