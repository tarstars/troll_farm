# D43 binary closed-loop policy-improvement preflight — result (2026-07-21)

## Verdict

**Reject the frozen binary PPO recipe and do not open the long run.** The preflight is mechanically
clean and learns a measurable aggregate preference, but it fails the required state-dependent
movement gate. Across the fixed 512-state probe, rank-one probability moves from exactly 0.2500 to
0.2681 on average while its final standard deviation is only **0.001164**, below the frozen 0.005
floor. Deterministic rank-one choices remain zero.

This is not an environment, parallelism, legality, reward, or serialization failure. Fourteen of
fifteen substantive gates pass, and the recovery checkpoint is bit-identical to the first completed
run. The failure localizes D43 to a nearly uniform probability shift rather than useful conditional
choice. Per the frozen protocol, changing initialization probability, duration, learning rate,
model width, or eligibility thresholds within this recipe is closed. No long training,
development bank, candidate, TestSession, submission, or Arena action opens.

## Frozen execution and integrity

- The run completes exactly 32 updates and **131,072 transitions** with 64 environments x 64 steps.
- It observes **1,321 eligible states**, samples 343 alternatives, and has a 25.965% alternative
  rate. There are zero noneligible deviations and zero illegal actions.
- **778 episodes** complete. Worker-two, worker-three, and crop rates are 98.46%, 91.00%, and 100%;
  these are descriptive preflight telemetry rather than a development comparison.
- Maximum telescoping reward-identity error is `9.6634e-6`, below the `1e-4` limit. All losses,
  eligible KL values, clip fractions, and rewards are finite.
- The 1,249-parameter actor drifts by L2 **0.31449**, proving that optimization updates it.
- End-to-end throughput is **761.999 transitions/s** over 172.01 wall seconds. CPU time is 2,829.26
  seconds, or **16.45 effective cores**, comfortably clearing the 12-core and 400-transition/s
  gates.

## Mechanical gate result

| Gate family | Result | Verdict |
|---|---:|---|
| exact transition/update budget | 131,072 / 32 | pass |
| eligible states / sampled alternatives | 1,321 / 343 | pass |
| alternative rate | 25.965% | pass |
| illegal / noneligible deviations | 0 / 0 | pass |
| complete episodes | 778 | pass |
| reward identity | maximum `9.6634e-6` | pass |
| actor L2 drift | 0.31449 | pass |
| probe mean movement | +0.018121 | pass |
| probe probability standard deviation | **0.001164** | **fail** |
| effective CPU / throughput | 16.45 cores / 761.999 transitions/s | pass |
| recovery checkpoint equality | every model tensor equal | pass |

The final probe probabilities span only 0.26360--0.26997. Although PPO raises the average chance
of rank one, it does not separate the 512 states enough to satisfy the deliberately minimal
conditional-movement requirement.

## Multilevel diagnosis

### Infrastructure and compute

The exact-prior macro environment, binary action interface, actor-only eligibility mask, critic,
telescoping reward, vector rollout, and 20-thread backend all work together. CPU utilization is no
longer a bottleneck: the measured 16.45 effective cores and 762 transitions/s are sufficient for a
long local run if a learning design earns one.

### Optimization

The actor is not frozen: its parameter drift, sampled alternatives, finite losses, and +0.018 mean
probe movement all pass. The observed change is nevertheless almost constant across states. The
short on-policy signal estimates that alternatives are somewhat more useful in aggregate, but it
does not learn which eligible states should take them.

### Credit assignment and data geometry

Only 1,321 of 131,072 transitions, about **1.01%**, contribute actor loss. Those states share a
positive but noisy action reservoir established by D41f/D42. Terminal telescoping rewards and a
single sampled binary action provide enough evidence to shift the global alternative prior, but
not enough low-variance contrast to learn a contextual boundary in 32 updates. This is consistent
with D41g--D42: expected value exists, while individual outcome sign is difficult to infer from a
snapshot.

### Strategy

D43 does not disprove rank-one rate interventions or closed-loop improvement. It rejects this
specific sparse Bernoulli PPO formulation as the next scalable route. D40 remains the complete
teacher/resident-side strategic anchor, and the D41f value region remains useful evidence. The next
learning abstraction should expose a stronger per-decision contrast—such as paired/counterfactual
continuation advantage or a structured multi-action value objective—before another closed-loop
policy run is authorized.

## Serialization recovery

The first execution completed all transitions and saved its checkpoint, then Python JSON encoding
rejected a NumPy boolean derived from the reward-identity scalar. Before rerunning, a separate
recovery protocol froze the sole permitted scalar conversion and required every recovered model
tensor to match the preserved checkpoint exactly. The recovered and original checkpoints both
have SHA-256
`ae25f7a889ffe74a203bccefdc1140bd5d436091d63f0342612a5ec02550b469`.
The equality gate passes, so the report is a deterministic recovery of the completed experiment,
not a second selected training outcome.

## Decision and next hypothesis

Do not extend D43 or tune its failed movement gate. Close sparse binary PPO over this eligibility
reservoir. The next protocol should first test whether paired continuation estimates can produce a
stable state-dependent advantage ranking on fresh maps, with repeated-rollout variance and
closed-loop compounding measured explicitly. Only a prospective complete-policy gain should reopen
long training or candidate construction.

## Evidence

- frozen protocol SHA-256:
  `20c544d6c454d8966b4a5c32b54f844af04c03b41f059462566b5cd363eaec28`;
- recovery protocol SHA-256:
  `5564c628cdd59f634e8dc8804c8573c02466ea06f373bb5d29bef93b599c04af`;
- result JSON SHA-256:
  `12bac7491b67e118d9d90baf3895b8a1165b1f7b8335572956039608e352661e`;
- original and recovered checkpoint SHA-256:
  `ae25f7a889ffe74a203bccefdc1140bd5d436091d63f0342612a5ec02550b469`;
- trainer SHA-256:
  `6d8f330e19ac24c79a3ef07b7ee05083892886f883f1f2e24923862774641072`;
- focused trainer tests: six passed, together with the D41c environment tests.
