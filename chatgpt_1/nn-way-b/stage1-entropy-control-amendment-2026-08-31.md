# Stage 1 amendment: entropy needs a fresh paired control

Date: 2026-08-31
Agent: `chatgpt_1`
Task: `20260829-nn-bot-way-b`
Amends:

- `agent/chatgpt_1@018ab8c0a0d20886002397e0a4dda36e21048971`
- `chatgpt_1/nn-way-b/self-play-training-recovery-review-and-staged-plan-2026-08-31.md`

## Correction

The original Stage 1 proposed one new entropy-zero run compared against historical run I. That is not a clean causal experiment after Gate 0.

Gate 0 changes the trainer by repairing target-KL aggregation and adding telemetry. Telemetry should be inert, but the target-KL repair can change epoch stopping and therefore the parameter trajectory. Historical run I was also generated under an earlier exact code pin. Unless a matched-seed non-regression proves the repaired trainer reproduces run I bit for bit through the tested horizon, comparing a new treatment with old run I changes more than entropy.

## Correct Stage 1 design

Launch two fresh arms from the same clone under the same integrated post-Gate-0 code:

```text
CONTROL E01: entropy_coef = 0.01
TREATMENT E00: entropy_coef = 0.00
```

Everything else must be identical:

```text
initial and anchor checkpoint
train_scope = plan-critic
TROLL executor = masked argmax
executor tensors frozen
seed and episode-seed stream
maps and champion-only opponent
num_envs and rollout_steps
gamma and lambda
reward definition and scale
critic warm-up
actor and critic learning rates
anchor schedule
target-KL rule
update/minibatch order
checkpoint budgets
```

Run I remains historical context, not the causal control.

## Gate amendment

Read both fresh arms at the same update budgets. The primary treatment effect is:

```text
E00 - E01
```

on the same locked map-seat cells.

`ENTROPY_CONFIRMED` requires all of:

1. executor tensors remain byte-identical in both arms;
2. on the 192-cell confirmation panel at updates 1,500 and 2,500, E00 has a positive paired mean score-margin delta versus E01;
3. the pooled 384-cell episode-cluster/paired bootstrap interval for `E00 - E01` has lower bound above zero;
4. E00 has higher clone top-1 plan agreement and lower or equal plan entropy than E01 at both budgets;
5. E00 does not merely become more deterministic around a worse action: unsupported-plan selections, purchase success, final score and activity metrics must not regress;
6. legality, timeout and loop gates remain clean.

`ENTROPY_NOT_CONFIRMED` if the paired interval includes zero, the treatment effect reverses, or both arms drift similarly.

## Cheap prerequisite

Before the full paired run, execute a 10-update matched-seed control proving that:

- E01 under the integrated post-Gate-0 trainer is deterministic;
- new telemetry alone does not change tensors or optimizer state;
- any target-KL behavior change is recorded rather than assumed absent.

If the historical run-I pin and the repaired E01 arm happen to stay bit-identical through all tested updates, historical run I may be shown as an additional replication. It must not be the only control.

No run or platform action was taken by this amendment.
