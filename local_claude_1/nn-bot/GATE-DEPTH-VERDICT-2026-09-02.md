# Gate verdict — the doubled budget (depth), s22L against s22, end against end (2026-09-02 18:0xZ)

**Verdict of record: `DEPTH_NOT_CONFIRMED` by the frozen letter** — the win-rate interval's lower bound
sits at exactly zero, so it is not "wholly above zero"; positive at each measurement, clone
non-inferiority held with room. (The gate program prints `ENTROPY_NOT_CONFIRMED`; its four outcome
names were frozen for the entropy test and its rule is variable-agnostic, printed with the verdict.)
The doubled-budget arm's end is nonetheless **the highest-scoring artefact of the programme so far:
37 of 144 at both of its ends**, against the standard budget's 33 and 33, with a margin of +5.9 points
per cell whose interval is clear of zero.

## The question (pre-registered blind, `PREREG-2026-09-02-depth-rollout512.md`, Gate A)

Is the stack (wood 2 + 2, rollout 128) trained at a doubled budget a better artefact *at its end* than
the same stack at the standard budget at its end? The trainer anneals the learning rate to zero over
the whole budget, so the only like-for-like comparison of two budgets is end against end: treatment
`ppo-yt-s22L` at updates **5,250** and **5,419** (its last regular and its final checkpoint), control
`ppo-yt-s22` at **2,500** and **2,709**. Same clone, same seed, same 6,218-map slice byte for byte
(verified inside both payload tarballs), the trainer arguments differing in `--total-turn-steps`
(22,200,000 vs 11,100,000) and the run name only.

## The numbers (the locked 144-cell panel, the same cells for every number; 0 faults anywhere)

| measurement | s22L (doubled budget) | s22 (standard budget) | the clone |
|---|---|---|---|
| 1 = s22L@5,250 vs s22@2,500 | **37 of 144** (score 142.5 vs the champion's 188.8) | 33 of 144 (136.6 vs 189.2) | 26 of 144 |
| 2 = s22L@5,419 vs s22@2,709 | **37 of 144** (142.3 vs 189.1) | 33 of 144 (136.5 vs 188.8) | 26 of 144 |

- Paired effect s22L − s22 per cell: **+0.028, 95 % interval [0.000, +0.063]** (10,000 clustered
  bootstrap draws over the 144 map-seat units, both measurements carried together, `PYTHONHASHSEED=0`).
  The lower bound is exactly zero — the same shape as the host replication of the reward path on 09-01
  (+0.049 [0.000, +0.101]); the frozen letter calls it not confirmed.
- Positive at each measurement: **yes** (+0.028 and +0.028).
- Clone non-inferiority: **holds with room** — s22L loses 2 cells the clone won and wins 14 the clone
  lost, **net +12 cells** (budget: at most 6 net lost).
- Margin (not the gate): **+5.9 points per cell, [+1.9, +10.1]**.
- Hash-seed sensitivity, measured as the pre-registration requires: under 40 hash seeds the interval
  is [0.000, +0.063] in all 40 and the verdict is the same in all 40. The verdict does not depend on
  the seed.

## What it says

The doubled budget buys about four cells of 144 (2.8 percentage points of win rate) and six points of
margin at the end of training, and the artefact is the best the programme has produced; the gain is
too small for the frozen gate to call it at this panel size. Depth and schedule are confounded inside
"doubling the budget" (the anneal caveat in the pre-registration), so this reads as "the longer
schedule's end is at least as good and probably a little better", not as a mechanism. The exploratory
reads pre-registered beside the gate — s22L at 1,500 / 2,500 against s22 at the same ages (the schedule
effect at matched age) and the curve at 3,000 / 4,000 — are benched next and labelled exploratory.

## Reproducibility notes

- Arm: `ppo-yt-s22L`, operation `371ec5d0-7528153d-42e03e8-30941f24` (the relaunch with s22's map slice;
  the first launch of 04:54Z, which carried a grown corpus, was aborted while queued), completed after
  271.6 minutes, retrieved to `yt_work/ppo/ppo-yt-s22L-output/` (archive sha256 `e2cfebe6…`).
- Benches: `bench_ages.py`, identical flags to every other arm (locked panel `locked-panel-seed1.jsonl`,
  the champion's file `0e92f8fa…`, seed 0, train-p 0.02, argmax decoding), run 17:12Z–17:55Z on the host
  at nice 19 with the two host arms training beside them.
- Gate: `PYTHONHASHSEED=0 gate1.py --treatment 1=bench-s22L-locked-u5250.json --treatment 2=bench-s22L-locked-u5419.json --control 1=bench-s22-locked-u2500.json --control 2=bench-s22-locked-u2709.json --clone bench-clone-locked.json`;
  verdict JSON `results/entropy-gate-0901/gate1-verdict-s22L-depth.json`.
- The ledger (wins of 144 on the locked panel): clone 26 · r22 31 / 29 · s22 29 / 33 / 33 ·
  **s22L 37 / 37 (its ends)** · s512 33 / 36 · parity bar 72.
