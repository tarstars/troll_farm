# Curriculum Level 1 online teacher-auxiliary result — 2026-07-19

## Verdict

The coefficient-0.10 online teacher auxiliary fixes deterministic PPO mode collapse on the exact
paired consumed experiment. It passes Stage A, the one-million-transition final gate, and the
post-run action gate. This is strong causal mechanism evidence, but it is not yet independent
confirmation. One frozen fresh-seed run is authorized before Level 2.

No Arena submission or resident change is authorized.

## Paired causal result

Both rows start from the same seed-47 behavior clone, use PPO training seed base 3,100,000, and are
evaluated on exactly seeds 2,001,000--2,001,999. The sole learning change is auxiliary
cross-entropy coefficient 0.10 on the deterministic teacher action at every rollout state.

| 250k result | Pure PPO | Teacher-auxiliary PPO |
|---|---:|---:|
| Overall success | 18.2% | 97.1% |
| Nonzero-deficit success | 9.13% | 96.77% |
| Height floor | 15.32% | 94.76% |
| Median successful turn | 1 | 42 |
| Paired teacher median delta | 0 | 0 |

The +81.1 percentage-point recovery on an otherwise identical run identifies the missing
constraint. Stochastic rollout success alone hid the failure; online teacher agreement preserves
the deterministic action ordering that deployment uses.

## Full-schedule result

At one million transitions, the auxiliary policy achieves:

- 993/1,000 overall success;
- 99.22% nonzero-deficit success;
- 98.39% worst map-height bucket;
- median successful completion at turn 41;
- zero paired median delay to the exact teacher;
- 4,213 HARVEST selections in 5,657 legal HARVEST opportunities, or 74.47%;
- 1,985 `MOVE current` waits, versus 119,551 for failed pure PPO.

Late training retains roughly 95% teacher-action accuracy while critic explained variance reaches
about 55--60%. The auxiliary therefore does not merely freeze the clone: the value function and
PPO objective continue learning while the actor stays inside a teacher-supported action manifold.

Wall time is 1,540.16 seconds, aggregate host CPU 69.46%, and end-to-end throughput 649.3
transitions/s. The added supervised objective is computationally affordable; sustained CPU
frequency, not label generation, is the limiting resource.

## Frozen artifacts

- protocol:
  `c7f1b8e52accbdf386615b0f424c1a5fb3571dbfd9ad4f68275b67410c1c8de6`;
- Stage A checkpoint:
  `a077c3382f415f4296ebf4f9d8b9e1c6d4f85b66c6fc671988906280ed287924`;
- Stage A evaluation:
  `82a83af0b20d448f5e8d75b9f9a639f305cf707f3202c202198e3be9f475474e`;
- final checkpoint:
  `762c45d421288c50be5282e16dc89e1fa97249dbd8c1d9afe62c84a253ac3331`;
- final evaluation:
  `aa3af23b7a8c1ba5bfb00b9bf4729dced7fd4e97f364db15b1514bdcafd7c72d`;
- exact action audit:
  `fd6e9e420817aba9faacd23174ed580b802ce59c932919f024ac36a4a44bd610`;
- training summary:
  `d59a5b08da1058cea45965833f0f00023bf6ab5740f176658178cdd557cc4da8`.

## Conclusion at multiple levels

- **Action level:** the auxiliary restores HARVEST over wait at legal work states.
- **Trajectory level:** deterministic nonzero-deficit success returns from 9.13% to 96.77% at the
  paired 250k checkpoint.
- **Optimization level:** supervised actor anchoring and PPO value learning coexist; pure PPO is
  too seed-sensitive.
- **Architecture level:** BFS distance planes plus online teacher support are the minimum current
  Level 1 learner. Behavior cloning or PPO alone is insufficiently robust.
- **Contest level:** this still models one fixed worker against a waiting opponent. It validates
  the learning loop, not renewable economy or field strength.

## Next move

Run one independent confirmation with model seed 53, BC stream 4,000,000, PPO stream 4,100,000,
and exact fresh evaluation bank 2,002,000--2,002,999. The auxiliary coefficient and all other
settings remain fixed. A full pass unlocks randomized-worker Level 2; a failure closes this
formulation without coefficient tuning.

