# Gate verdict — the doubled budget on the host, hs22L against hs22, end against end (2026-09-03 07:4xZ)

**Verdict of record: `DEPTH_HOST_NOT_CONFIRMED` by the frozen letter** — the win-rate interval contains
zero and the effect is not positive at each measurement (zero at the second); clone non-inferiority held.
(The gate program prints `ENTROPY_NOT_CONFIRMED`; its outcome names were frozen for the entropy test; the
rule is variable-agnostic and printed with the verdict.) **The cluster's reading of the same lever (37 / 37
against 33 / 33, +0.028 [0.000, +0.063]) does not replicate on the host and the full map corpus.**

## The question (the same gate as Gate A, with the host files, as the pre-registration said)

Is the stack trained at a doubled budget a better artefact *at its end* than the stack at the standard budget
at its end, on the second platform (this laptop, 7 threads, the pinned 31,088-map corpus copy)? Treatment
`ppo-host-s22L` (`…-0902c`, 5,419 updates, finished 09-02 23:4xZ) at updates **5,250** and **5,419**; control
`ppo-host-s22` (`…-0902c`, 2,709 updates) at **2,500** and **2,709**. Same clone, same seed, same corpus byte for
byte; the arguments differ in `--total-turn-steps` (22,200,000 vs 11,100,000) and the run name only.

## The numbers (the locked 144-cell panel, the same cells for every number; 0 faults; benched on the VM
under the owner's compute rule, `/home/tarstars/venvs/nn-bot`, the VM-built referee library)

| measurement | hs22L (doubled budget) | hs22 (standard budget) | the clone |
|---|---|---|---|
| 1 = hs22L@5,250 vs hs22@2,500 | **33 of 144** (score 137.3 vs the champion's 189.4) | 32 of 144 (138.0 vs 190.3) | 26 of 144 |
| 2 = hs22L@5,419 vs hs22@2,709 | **33 of 144** (137.5 vs 189.5) | 33 of 144 (138.3 vs 189.0) | 26 of 144 |

- Paired effect hs22L − hs22 per cell: **+0.003, 95 % interval [−0.024, +0.028]** (10,000 clustered bootstrap
  draws over the 144 units, both measurements together, `PYTHONHASHSEED=0`). Contains zero.
- Positive at each measurement: **no** (+0.007 and 0.000).
- Clone non-inferiority: holds — 2 cells lost that the clone won, 9 gained, net +7.
- Margin (not the gate): −0.6 points per cell, [−3.5, +2.4].

## What it says, with the cluster beside it

| platform | corpus | doubled budget at its ends | standard budget at its ends | effect |
|---|---|---|---|---|
| cluster (Gate A, 09-02) | 6,218-map slice | 37 / 37 | 33 / 33 | +0.028 [0.000, +0.063] |
| host (this gate) | 31,088 maps | 33 / 33 | 32 / 33 | +0.003 [−0.024, +0.028] |

Two readings of one lever, neither confirmed, the second flat: the doubled training budget is not a lever we
can confirm on either platform, and the cluster's four extra cells sit inside what the panel's noise allows
(the frozen interval's lower bound was exactly zero there). The programme's ledger keeps s22L's cluster end as
the best raw count (37) and does not promote it; the recipe stays 2 + 2 with the 128-step rollout at the
standard budget. What remains open on the depth question is the stacked arm (`ppo-yt-s22L512`, Gate D,
pre-registered, running on the cluster), which asks whether the long look-ahead adds at the doubled budget.

## Reproducibility notes

- Arms: `/home/tarstars/nn-data/ppo-host-s22L-0902c/` (5,419 updates; `ppo-host-s22L-training-summary.json`)
  and `/home/tarstars/nn-data/ppo-host-s22-0902c/` (2,709).
- Benches: `bench_ages.py --tag hs22L-locked --ages 5250,5419` on the VM (`troll-vm`, 4 cores, `--jobs 1
  --threads-per-job 2 --nice 19`, `/data/scratch/hs22L/results/`), 09-03 06:0xZ–07:3xZ, the referee library
  copied from claude_1's VM worktree (the `rust/` source identical to `main`); the same flags as every other
  bench (locked panel `locked-panel-seed1.jsonl`, the champion's file `0e92f8fa…`, seed 0, train-p 0.02, argmax).
- Gate: `PYTHONHASHSEED=0 gate1.py --treatment 1=bench-hs22L-locked-u5250.json --treatment 2=bench-hs22L-locked-u5419.json --control 1=bench-hs22-locked-u2500.json --control 2=bench-hs22-locked-u2709.json --clone bench-clone-locked.json`;
  verdict JSON `results/entropy-gate-0901/gate1-verdict-hs22L-depth.json`.
- Ledger (wins of 144): clone 26 · r22 31/29 · s22 29/33/33 · s22L 31/34/35/31/37/37 · s512 33/36 ·
  hr22 28/31 · hs22 30/32/33 · **hs22L 33/33** · parity bar 72.
