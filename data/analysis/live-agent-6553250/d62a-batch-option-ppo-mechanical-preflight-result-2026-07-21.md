# D62a batch-option PPO mechanical preflight — result (2026-07-21)

## Verdict

**Reject and close this feed-forward PPO recipe.** The exact semi-Markov environment and learning
pipeline pass their mechanical, parity, utilization, coverage, and continuous-movement gates, but
the final policy remains deterministically balanced on all 512 frozen probe states. It therefore
fails both discrete state-conditioned movement gates. Two of 1,669 completed episodes also create
no crop, failing the universal crop gate.

Per the frozen decision rule, do not extend training or tune initialization, entropy, width,
learning rate, or the 131,072-transition budget. The checkpoint is infrastructure evidence only;
it is not eligible for value evaluation, candidate construction, TestSession, submission, or
Arena.

## Frozen evidence

- protocol SHA-256: `e59c5eb06d8a8742de6017226c7ed79378b17bc7db512f6e70f021d04992d4cb`
- deployable-balanced reference amendment SHA-256:
  `ff34a05920e25b4777bbc11424affb61607b00b93815ae93051113e6a311a41d`
- Rust batch environment SHA-256:
  `dc476cdccd5076a9f6837190a60e53941db59ce80e94fc528df98b30d3e3dde3`
- Python ABI wrapper SHA-256:
  `f5248c0daa14456431092b7c6b0c2f620c2dffd3909f65e28d75538deddb4018`
- release library SHA-256:
  `0b2dbc8d23f67f975e584f9b7f6e69f91dc13397dca8a24fe54aa262e760b0f7`
- parity validator SHA-256:
  `e7abedeb0ca17513b9764c031627344c45dd2893dfd1aaf1942b668efe82e660`
- parity result SHA-256:
  `dd44181094a534a17feb2352a6ffa315110046ea34cf192db20f0eb5344e7c56`
- trainer SHA-256: `09be2dcd6375e9a14855eb06934d6b3882796a89beaea8517e84ecdd0c6105d6`
- final checkpoint SHA-256:
  `f2400b7fabe87ba06786f8a490b99fa13e43828503d0c8799bcc9b0b05bfb283`
- machine-readable result SHA-256:
  `2da50a9d3caaa0390a13f3e8de3ba9a43faa86f216f63ea0153a8f505432eb57`

The initial attempt stopped before optimization because a diagnostic compared float32 softmax
probabilities to decimal targets with a `1e-7` tolerance; the largest representation difference
was about `1.2e-7`. Only that diagnostic tolerance was changed to `1e-6`. No checkpoint or result
existed, and no protocol parameter, sampled action, transition, seed, or optimizer update was
consumed before the final run.

## Environment parity

D61's corrected `safe_balanced` row is a special direct-D40 control, while a deployable linear
policy choosing balanced still traverses the renewable-safe candidate filter. The pre-result
amendment therefore created one zero-weight D61 linear reference, whose strict ties always choose
balanced, and left the D61 runner unchanged.

Two independent environment passes match all frozen D61 references exactly:

- 4 modes × 16 tasks = 64 terminal comparisons;
- own score, opponent score, workers, created crops, action hash, and state hash all match;
- repeat terminal fields are bit-exact;
- mismatches: 0; and
- maximum reward-telescoping error: `8.3223e-6` points.

This establishes that the PPO environment implements deployable D61 option semantics; it does not
establish policy value.

## Mechanical execution

The final-only run completes the exact 32 updates and 131,072 transitions:

| Measure | Result | Gate |
|---|---:|---:|
| Completed episodes | 1,669 | ≥1,500, pass |
| Unlocked transitions | 110,753 / 131,072 = 84.50% | ≥20%, pass |
| Sampled non-balanced | 21,944 / 131,072 = 16.74% | ≥5%, pass |
| Worker-three episodes | 90.71% | ≥85%, pass |
| Crop-creating episodes | 1,667 / 1,669 = 99.88% | 100%, **fail** |
| Illegal actions | 0 | zero, pass |
| Direct/provenance/deposit failures | 0 / 0 / 0 | zero, pass |
| Maximum reward-identity error | `9.2313e-6` | `<1e-4`, pass |
| Actor parameter L2 drift | 1.0632 | ≥0.05, pass |
| Throughput | 679.25 transitions/s | ≥400, pass |
| Effective CPU use | 16.56 cores | ≥12, pass |

All observations, rewards, losses, gradients, and final parameters are finite. The terminal stream
SHA-256 is `2c49b95e6206279dada19606219210fe83cd4a26964db18c17566ce5e7e79e38`.
Invalidated jobs total 5,199 but are legitimate transactional replanning events, not direct,
provenance, or deposit-prediction failures.

## State-dependent movement probe

Continuous movement is real but insufficient for a deterministic controller:

| Probe measure | Initial | Final | Gate |
|---|---:|---:|---:|
| Mean balanced probability | 0.8500 | 0.7449 | descriptive |
| Mean harvest probability | 0.0500 | 0.0463 | descriptive |
| Mean renew probability | 0.0500 | 0.0876 | descriptive |
| Mean fell probability | 0.0500 | 0.1211 | descriptive |
| Mean total non-balanced probability | 0.1500 | 0.2551 | change +0.1051, pass |
| Non-balanced probability std across states | 0 | 0.01162 | ≥0.01, pass |
| Deterministic non-balanced states | 0 | 0 / 512 | ≥16, **fail** |
| Distinct deterministic non-balanced modes | 0 | 0 | ≥2, **fail** |

Final total alternative mass ranges from 0.2113 to 0.2802 across the probe, so the actor has learned
a state-dependent preference surface. It has not overcome the balanced prior enough to change a
single deterministic decision. Deploying stochastic sampling would be a different controller and
is not authorized by this result.

## Multilevel interpretation

1. **Mechanics:** the four-action semi-Markov abstraction is exact, fast, parallel, and dense enough
   to train. Environment construction is no longer the bottleneck.
2. **Optimization:** short on-policy terminal-return PPO changes probabilities substantially but
   does not turn D61's heterogeneous hindsight value into deterministic decisions. More updates or
   a weaker prior would be post-result tuning of this consumed recipe, so they are closed.
3. **Safety:** “only balanced before a live own crop” is a legality mask, not an establishment
   guarantee. Rare D40 trajectories can finish without ever creating a crop; the 128-task D61 panel
   did not expose this 2/1,669 tail. A future representation must model establishment as a positive
   invariant rather than infer it from banning semantic alternatives.
4. **Strategy:** D61 proves useful option vocabulary and state heterogeneity; D62 shows that this
   compact observation plus short undifferentiated on-policy return is not enough to recover the
   conditional chooser. The headroom remains, but this training recipe cannot claim it.
5. **Field transfer:** no further long local training is justified before learning how current
   Legend games populate these 56 features and option boundaries. Fresh passive replay collection
   is now the highest-priority discriminator.

## Post-result no-crop classification

A frozen 2,048-task filtered-balanced audit recovers exactly two zero-crop rows: both seats of seed
`9802022` against `resident` (task indices 352 and 360). They stall after all plants disappear at
turns 143/147. They are not infeasible cases: each starts with `[10,2,2,5]` seed stock, the opponent
creates six crops, and our controller selects two renewal jobs but materializes none. Thus the
99.88% aggregate hides one symmetric map/controller failure, and the 100% feasibility-conditioned
establishment gate remains appropriate. See `d62a-no-crop-tail-audit-result-2026-07-21.md`.

## Next eligible move

Proceed with the already frozen D61p snapshot-safe passive replay refresh, once explicitly
authorized: current resident agent `6561795`, ten recent games from each current top-20 Legend
agent, and visible Boss games. Parse and QA them immutably, freeze discovery/validation/confirmation
splits, then measure feature shift, rare no-establishment states, worker-transition regimes,
opponent coverage, and outcome-blind option activation.

Until that evidence exists, do not start D62b, train a longer PPO, relax deterministic gates,
construct a candidate, or perform any platform action.
