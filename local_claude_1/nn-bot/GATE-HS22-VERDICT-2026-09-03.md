# Gate verdict — the host replication of the stack, hs22 against hr22 (2026-09-03 04:4xZ)

**Verdict of record: `STACK_HOST_NOT_CONFIRMED` by the frozen letter** — the win-rate interval contains zero;
positive at both ages; clone non-inferiority held. (The gate program prints `ENTROPY_NOT_CONFIRMED`; its
outcome names were frozen for the entropy test; its rule is variable-agnostic and printed with the verdict.)

## The question (Gate C of `PREREG-2026-09-02-depth-rollout512.md`)

Does the stack (wood 2 + 2 with the 128-step rollout) beat the reward-path arm alone (wood 2 + 2 with the
32-step rollout) on the second platform and the full 31,088-map host corpus, as the cluster's s22-vs-r22 read
suggested (+0.007 [−0.021, +0.035], rising 29 → 33)? Treatment `ppo-host-s22` (run `…-0902c`, relaunched on
mains 09-02 12:2xZ, 2,709 updates, finished 09-02 ~20:35Z), control `ppo-host-hr22`; both from the pinned
09-01 corpus copy, both 7 threads at nice 15; the arguments differ in `--rollout-steps 128 --num-envs 32`
versus 32 × 128 and the run name only.

## The numbers (the locked 144-cell panel; 0 faults)

| update | hs22 (the stack, host) | hr22 (reward path alone, host) | the clone |
|---|---|---|---|
| 1,500 | **30 of 144** (score 136.6 vs the champion's 189.5) | 28 of 144 (132.7) | 26 of 144 |
| 2,500 | **32 of 144** (138.0 vs 189.2) | 31 of 144 (135.4) | 26 of 144 |

- Paired effect hs22 − hr22 per cell: **+0.010, 95 % interval [−0.021, +0.042]** (10,000 clustered bootstrap
  draws over the 144 units, both ages together, `PYTHONHASHSEED=0`). Contains zero.
- Positive at each age: **yes** (+0.014 and +0.007).
- Clone non-inferiority: **holds** — net +8 cells over the clone (budget: at most 6 net lost).
- Margin (not the gate): +2.7 points per cell, [−0.7, +5.9].
- hs22 at its end (2,709) is benched beside them for the ledger.

## What it says

The host replicates the cluster's shape to the digit: the stack over the reward path alone is a small positive
that the panel cannot separate from zero (+0.010 here, +0.007 on the cluster). The recipe stays 2 + 2 with the
128-step rollout because it never reads worse and reads better at every age on both platforms, not because a
gate confirmed the rollout term. The host ledger: hr22 28 / 31 · hs22 30 / 32 (the cluster: r22 31 / 29 ·
s22 29 / 33 / 33); the clone 26; parity bar 72.

## Reproducibility notes

- Arm: `/home/tarstars/nn-data/ppo-host-s22-0902c/` (checkpoints every 250, `ppo-host-s22-training-summary.json`).
- Benches: `bench_ages.py --tag hs22-locked --ages 1500,2500,2709` at nice 19, 09-03 04:0xZ–04:4xZ.
- Gate: `PYTHONHASHSEED=0 gate1.py --treatment 1500=bench-hs22-locked-u1500.json --treatment 2500=bench-hs22-locked-u2500.json --control 1500=bench-hr22-locked-u1500.json --control 2500=bench-hr22-locked-u2500.json --clone bench-clone-locked.json`;
  verdict JSON `results/entropy-gate-0901/gate1-verdict-hs22.json`.
