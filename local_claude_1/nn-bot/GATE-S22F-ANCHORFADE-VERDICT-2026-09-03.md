# Gate verdict — the anchor fade, s22F against s22 (2026-09-03 12:1xZ)

**Verdict of record: `ANCHORFADE_NOT_CONFIRMED` by the frozen letter** — the win-rate interval contains zero and the
effect is not positive at each age (+0.049 at 1,500, −0.028 at 2,500); clone non-inferiority held with room. (The
gate program prints `ENTROPY_NOT_CONFIRMED`; its outcome names were frozen for the entropy test; its rule is
variable-agnostic and printed with the verdict.) **The pre-registered ruling applies (Gate E, written 08:4xZ before
the run): the "self-play from the clone" road is closed in this form; the network line's next signal is the opening
solver's schedules as a teacher — a design step, not a tuning arm.**

## The question (Gate E of `PREREG-2026-09-02-depth-rollout512.md`)

Does the stack, with the clone anchor faded linearly to zero over the run instead of held near 0.1, move further than
the anchored stack — or collapse, as full-parameter self-play did? Treatment `ppo-yt-s22F` (op `bd54fcc2…`, started
08:28Z, 2,709 updates, no preemption): s22's arguments with `--anchor-coef-final 0.0 --anchor-decay-steps 11100000`;
control `ppo-yt-s22` (29 / 33 at 1,500 / 2,500); the same clone, seed and map slice byte for byte; the prepared
arguments differ in the two anchor fields and the run name only.

## The numbers (the locked 144-cell panel; 0 faults; benched on the VM under the owner's compute rule)

| update (anchor coefficient at that point) | s22F (anchor fading) | s22 (anchor held) | the clone |
|---|---|---|---|
| 1,500 (≈0.045) | **36 of 144** (score 141.8 vs the champion's 190.3) | 29 of 144 (136.7 vs 189.5) | 26 of 144 |
| 2,500 (≈0.008) | **29 of 144** (144.9 vs 193.8) | 33 of 144 (136.6 vs 189.2) | 26 of 144 |

- Paired effect s22F − s22 per cell: **+0.010, 95 % interval [−0.021, +0.042]** (10,000 clustered bootstrap draws
  over the 144 units, both ages together, `PYTHONHASHSEED=0`). Contains zero.
- Positive at each age: **no** (+0.049 at 1,500, −0.028 at 2,500).
- Clone non-inferiority: **holds with room** — 2 cells lost that the clone won, 18 gained, net +16.
- Margin (not the gate): +3.9 points per cell, [−0.1, +8.0]; the arm's own score is the highest of the programme at
  2,500 (144.9), while its win count fell — it scores more in the games it loses.

## What it says

Freeing the policy from the anchor moved it: the largest count at 1,500 of any arm (36) while the anchor was half its
starting strength, then a fall back to 29 by 2,500 as the anchor reached zero — drift beginning, not the collapse of
full-parameter self-play (the staged scope held the movement head frozen), and still above the clone. So the anchor
was holding the policy, and without it the plan head does not find a better place to settle at this reward; the
schedule's last thousand updates lose what the middle gained. Three outcomes were pre-registered; this is the third
(null / not confirmed): **the road is closed in this form** — no further tuning of the clone-anchored self-play recipe
is launched. The reward path (2 + 2) stays the only confirmed lever; the recipe stays 2 + 2, rollout 128, the anchor
held. The exploratory end (2,709) is benched on the VM for the ledger only.

## Reproducibility notes

- Arm: `ppo-yt-s22F`, operation `bd54fcc2-95c34640-42e03e8-6ee68d40`, completed after 136 minutes, retrieved to
  `yt_work/ppo/ppo-yt-s22F-output/` (archive sha256 `1d27643f…`); the anchor coefficient per update is in its log.
- Benches: `bench_ages.py --tag s22F-locked --ages 1500,2500` on the VM (`troll-vm`, two of four cores, nice 19,
  `/data/scratch/s22F/results/`), 10:54Z–12:0xZ, the same flags as every other bench (the locked panel, the champion's
  file `0e92f8fa…`, seed 0, train-p 0.02, argmax).
- Gate: `PYTHONHASHSEED=0 gate1.py --treatment 1500=bench-s22F-locked-u1500.json --treatment 2500=bench-s22F-locked-u2500.json --control 1500=bench-s22-locked-u1500.json --control 2500=bench-s22-locked-u2500.json --clone bench-clone-locked.json`;
  verdict JSON `results/entropy-gate-0901/gate1-verdict-s22F-anchorfade.json`.
- Ledger (wins of 144): clone 26 · r22 31/29 · s22 29/33/33 · s22L 31/34/35/31/37/37 · s512 33/36 · hr22 28/31 ·
  hs22 30/32/33 · hs22L 33/33 · **s22F 36/29** · parity bar 72.
