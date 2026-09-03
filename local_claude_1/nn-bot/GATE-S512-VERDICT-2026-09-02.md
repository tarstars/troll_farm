# Gate verdict — the 512-step rollout, s512 against s22 (2026-09-02 18:0xZ)

**Verdict of record: `ROLLOUT512_NOT_CONFIRMED` by the frozen letter** — the win-rate interval contains
zero; positive at each age, clone non-inferiority held with room. (The gate program prints
`ENTROPY_NOT_CONFIRMED`; its outcome names were frozen for the entropy test; the rule is
variable-agnostic and printed with the verdict.)

## The question (pre-registered blind, `PREREG-2026-09-02-depth-rollout512.md`, Gate B)

Does a four-times-longer rollout trace — 512 steps with 8 environments, the 4,096-sample batch held
— add to the stack (wood 2 + 2, rollout 128 with 32 environments)? The reviewer's "true long-horizon
credit" lever taken one step further: about 130–170 game turns of look-ahead. Treatment `ppo-yt-s512`,
control `ppo-yt-s22`, same clone, same seed, same 6,218-map slice byte for byte; the trainer arguments
differ in `--rollout-steps 512 --num-envs 8` and the run name only. Standard protocol: ages 1,500 and
2,500. The expectation written before the data: a guess in the same direction as lever 2 (+0.017,
not confirmed), with the risk that eight environments make each update's data more correlated.

## The numbers (the locked 144-cell panel, the same cells for every number; 0 faults anywhere)

| update | s512 (512-step rollout) | s22 (128-step rollout) | the clone |
|---|---|---|---|
| 1,500 | **33 of 144** (score 139.0 vs the champion's 189.8) | 29 of 144 (136.7 vs 189.5) | 26 of 144 |
| 2,500 | **36 of 144** (142.9 vs 189.5) | 33 of 144 (136.6 vs 189.2) | 26 of 144 |

- Paired effect s512 − s22 per cell: **+0.024, 95 % interval [−0.010, +0.063]** (10,000 clustered
  bootstrap draws over the 144 units, both ages together, `PYTHONHASHSEED=0`). Contains zero.
- Positive at each age: **yes** (+0.028 and +0.021).
- Clone non-inferiority: **holds with room** — 3 cells lost that the clone won, 14 gained, **net +11**.
- Margin (not the gate): **+4.0 points per cell, [+0.6, +7.7]**.
- Hash-seed sensitivity: under 40 hash seeds the lower bound is −0.010 (38 seeds) or −0.007 (2), the
  upper +0.059 or +0.063; the verdict is the same in all 40.

## What it says

The longer trace reads like lever 2 did: a small positive point estimate at both ages, a margin gain
clear of zero, a win-rate gain the panel cannot separate from noise. It rises with age (33 → 36) as
s22 did (29 → 33). It did not hurt through the correlation of its eight environments. Not a confirmed
lever on its own; a candidate for stacking on the doubled budget, since both read positive and neither
alone reaches the bar. The final checkpoint (2,709) is retrieved and can be benched as an exploratory
end-point if capacity allows.

## Reproducibility notes

- Arm: `ppo-yt-s512`, operation `50c1737e-2212e43a-42e03e8-a7d614ed`, completed after 221.3 minutes,
  retrieved to `yt_work/ppo/ppo-yt-s512-output/` (archive sha256 `0ec42c72…`).
- Benches: `bench_ages.py`, identical flags to every other arm, run 17:12Z–17:55Z at nice 19.
- Gate: `PYTHONHASHSEED=0 gate1.py --treatment 1500=bench-s512-locked-u1500.json --treatment 2500=bench-s512-locked-u2500.json --control 1500=bench-s22-locked-u1500.json --control 2500=bench-s22-locked-u2500.json --clone bench-clone-locked.json`;
  verdict JSON `results/entropy-gate-0901/gate1-verdict-s512.json`.
