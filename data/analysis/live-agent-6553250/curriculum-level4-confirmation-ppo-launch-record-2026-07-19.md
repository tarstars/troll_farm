# Curriculum Level 4 independent confirmation PPO — launch record, 2026-07-19

## Eligibility

The exact seed-89 confirmation transfer clone passes its frozen gate. Before launch, the frozen
protocol, teacher control, random control, and clone checkpoint reproduced their recorded SHA-256
digests. Focused validation passed:

- 11/11 Python Level-4 environment, cloning, and PPO tests;
- 5/5 Rust shared actor / Level-3/4 environment tests.

No prior confirmation PPO artifact or process exists. The launch therefore consumes the sole
authorized confirmation PPO stream beginning at 6,900,000.

## Frozen execution

```text
uv run --no-sync python -m cgauto.train_level1_ppo
  --curriculum-level 4
  --run-name random-recipe-renewable-confirmation-ppo
  --model-seed 89
  --train-seed-base 6900000
  --eval-seed-base 2017000
  --num-envs 100
  --rollout-steps 100
  --total-transitions 4000000
  --stage-a-transitions 1000000
  --eval-episodes 2000
  --max-turns 240
  --update-epochs 4
  --minibatch-size 1000
  --learning-rate 0.00025
  --gamma 0.99
  --gae-lambda 0.95
  --clip-coef 0.2
  --entropy-coef 0.01
  --value-coef 0.5
  --reward-scale 0.01
  --max-grad-norm 0.5
  --threads 14
  --target-kl 0.03
  --initial-checkpoint data/analysis/live-agent-6553250/curriculum-level4-random-recipe-renewable-confirmation-bc.pt
  --gate-profile level4
  --protocol data/analysis/live-agent-6553250/curriculum-level4-confirmation-protocol-2026-07-19.md
  --random-baseline data/analysis/live-agent-6553250/curriculum-level4-confirmation-random-2017000-2018999-exact.json
  --teacher-baseline data/analysis/live-agent-6553250/curriculum-level4-confirmation-teacher-2017000-2018999-exact.json
  --teacher-aux-coef 0.10
```

The process reads Stage A at exactly one million decisions. Failure stops automatically. A pass
continues the same optimizer/process unchanged to four million; no checkpoint selection or
adaptive relaunch is permitted.

## Zero-decision invocation correction

The first shell invocation used the script pathname and stopped during imports with
`ModuleNotFoundError: cgauto`. It created no output artifact, constructed no environment, and
consumed no training decision or seed. The executable form above was corrected to Python's module
entry point, which changes only package discovery; every frozen argument and input remains exact.
