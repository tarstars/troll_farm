# Curriculum Level 1 exact replicate result — 2026-07-19

## Verdict

Behavior cloning replicates, but pure PPO does not.  The exact replicate stops at its frozen
250,000-transition gate with 18.2% deterministic success, 9.13% nonzero-deficit success, and a
15.32% height floor.  The current teacher-initialized pure-PPO schedule is closed as a reproducible
Level 1 learner.  The preauthorized online teacher-auxiliary test is now eligible on consumed data.

No new live candidate was produced and no submission was authorized.

## Integrity and controls

- frozen protocol SHA-256:
  `9d15762bfa4e06b5f2671ecac77f8973975b5257d12201e245fcaf2eaad45a4a`;
- model seed 47, BC stream beginning at 3,000,000, PPO stream beginning at 3,100,000;
- exact learned evaluation seeds 2,001,000--2,001,999, each present exactly once;
- teacher control 99.8%, median 40, SHA-256
  `47a070b485389634d8671fb78f1c09014bec65247402b664214db5c353221cb0`;
- random-legal control 9.9%, SHA-256
  `eb791a9850b138409658c3a705cc4ccabfaf54d0cb89d9892ffd0581b82ec81c`.

The fresh bank was opened once at the predeclared Stage A point.  The run stopped automatically;
no final-bank look or hyperparameter adaptation occurred.

## Results

The replicate clone passes its consumed exact-debug sanity gate with 95.1% overall, 94.46%
nonzero-deficit, 92.0% height floor, median 38, and zero paired teacher delay.  Its checkpoint is
`4c6365f7c1f5ce0836c9583ccc2d55df934606c0d75f27b6a1b31ac693655f21`.

At PPO Stage A, stochastic training rollouts still report 91.7% recent success, but deterministic
evaluation solves only 182/1,000 exact fresh-bank episodes.  A post-failure diagnostic of the
frozen clone on that now-consumed bank solves 943/1,000, so the bank is not the cause.

| Exact diagnostic | Clone | Pure PPO Stage A |
|---|---:|---:|
| Overall success | 94.3% | 18.2% |
| Nonzero-deficit success | 93.65% | 9.13% |
| Height floor | 91.94% | 15.32% |
| Median successful turn | 41 | 1 |
| HARVEST / legal HARVEST opportunities | 4,191 / 5,681 | 473 / 123,634 |
| `MOVE current` waits | 4,292 | 119,551 |

The Stage A checkpoint SHA-256 is
`ad2e784617d79fac96e0ce5ec2cc3f99b962dabdd03b557e3e2ad29e846dcba9`; its exact action-audit
SHA-256 is `9488c3295e6b8e663b613860ae72584148ae763db9977da053cb910cdfe3c0e4`.

## Interpretation

This is deterministic mode collapse.  PPO retains enough probability on useful actions for
stochastic rollouts to complete, while a slightly higher logit on `MOVE current` becomes the
argmax at work states.  On deficit 1--8 episodes the deterministic policy averages roughly
126--139 waits.  Navigation remains available and DROP remains exact; the collapsed decision is
primarily HARVEST versus wait.

The failure also explains why a single successful seed-43 run was insufficient evidence.  The
same architecture and schedule can end near clone parity or collapse its deterministic mode,
depending on initialization and training stream.  More transitions, another model seed, or
checkpoint selection on the consumed bank would not address the mechanism.

## Next move

Repeat the seed-47 run on the identical consumed PPO stream with one frozen change: add online
cross-entropy to the deterministic teacher action on every rollout state.  This directly anchors
the argmax under covariate shift while leaving rewards, PPO, entropy, critic learning, and all
seed streams unchanged.  No fresh evaluation bank may be opened during this mechanism test.

