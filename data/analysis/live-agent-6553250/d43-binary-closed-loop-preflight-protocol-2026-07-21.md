# D43 binary closed-loop policy-improvement preflight — frozen protocol (2026-07-21)

## Question and scope

D41d, D41f, and D42 independently show positive expected value from rank-one early/late rate
actions, while D41g, D41h, and D42 show that isolated terminal sign is not reliably classifiable.
D41e also shows that repeated accepted actions compound rather than dilute. D43 therefore changes
the learning abstraction: optimize a repeated closed-loop binary policy directly from telescoping
margin reward, with D40 forced everywhere outside the proven action reservoir.

This protocol authorizes one short mechanical PPO preflight, tests, a diagnostic result, and a
noncandidate checkpoint. It does not authorize a long training run, development qualification,
confirmation, deployment generation, TestSession, submission, or Arena.

## Frozen choice interface

At each exact macro decision, derive D40 rank zero and rank one from the frozen exact prior. A state
is learnable only when all conditions hold:

- branch is `rate`;
- turn is early (`<100`) or late (`>=200`);
- there are at least two candidates; and
- the frozen D41c residual rank-one-minus-rank-zero gap is in [0.200,0.340].

At learnable states the policy chooses binary 0 = rank zero or 1 = rank one. Every other state is
forced to rank zero and contributes no actor loss or entropy. The D41c checkpoint is used only to
define the fixed eligibility reservoir; its logits are not the new policy logits.

## Frozen 154-feature actor state

Construct, in order:

1. rank-zero shared features 0--16 (17);
2. rank-zero candidate features 17--43 (27);
3. rank-one candidate features 17--43 (27);
4. rank-one minus rank-zero candidate features (27);
5. mean legal-candidate features 17--43 (27);
6. maximum legal-candidate features 17--43 (27);
7. frozen residual gap and candidate count / 768 (2).

Total actor input is 154 finite floats. No opponent ID, map, seat, task, outcome, or hash is an input.
The training-only critic retains D41c's 105 values: shared first 17 plus mean and maximum of all 44
legal-candidate features.

## Frozen model and initialization

The actor is `154 -> 8 ReLU -> 1 Bernoulli logit`, 1,249 trainable parameters. Orthogonally
initialize the hidden layer, set output weights to zero, and set output bias to `log(0.25/0.75)`.
Thus every eligible state initially samples rank one with probability 25%, while deterministic
argmax is exactly D40. The critic is D41c's training-only 105→64→32→1 MLP.

Use model/NumPy seed 4,310 and exact environment library SHA-256
`5839a7b888f2772e54a293a66ed5b186df378d5b8514f43a200898c8eef70173`. Eligibility uses D41c
checkpoint SHA-256 `1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a`.

## Frozen short PPO execution

- training maps begin at seed 9,776,000 and auto-advance indefinitely;
- 64 environments x 64 rollout steps = 4,096 transitions/update;
- exactly 131,072 transitions = 32 updates;
- four shuffled epochs, minibatch 1,024;
- Adam learning rate 0.00025, epsilon `1e-5`, constant during this preflight;
- gamma 1.0, GAE lambda 0.95, clip coefficient 0.10;
- value coefficient 0.5, eligible entropy coefficient 0.001;
- no teacher loss, behavior-cloning loss, prior logit, or KL penalty;
- gradient norm 0.5 and eligible approximate-KL epoch stop at 0.02;
- normalize actor advantages only across eligible rollout states; train critic on all transitions;
- 20 Torch/Rust CPU threads.

Capture up to the first 512 eligible 154-vectors as a fixed diagnostic probe. Their initial
probability is exactly 0.25; score the same vectors once with the final actor.

## Mechanical acceptance gates

The preflight passes only if:

1. initial deterministic actions are exactly D40 and actor/critic counts are 1,249/8,897;
2. at least 1,000 eligible states and at least 200 sampled rank-one actions occur;
3. sampled rank-one rate among eligible states is in [15%,35%], with zero noneligible deviations;
4. zero illegal actions, direct-command failures, provenance failures, deposit-prediction failures,
   worker-cap breaches, nonfinite rewards/losses, or terminal task drift;
5. maximum telescoping margin-reward identity error is at most `1e-4`;
6. at least 512 complete episodes telescope;
7. actor L2 drift is at least 0.01, final probe mean moves at least 0.005 from 0.25, and final probe
   probability standard deviation is at least 0.005;
8. all recorded policy/value losses, eligible KLs, and clip fractions are finite;
9. effective CPU use is at least 12 cores and end-to-end throughput at least 400 transitions/s; and
10. the entire fixed transition/update budget completes exactly.

A pass proves only that the new interface fixes D41c's exploration/gradient barrier. It opens one
separately frozen long run with development gates. A fail closes this binary PPO recipe without
changing initialization probability, duration, learning rate, model size, or movement thresholds.
