# Gate 1 verdict — the entropy bonus does not matter (2026-09-01 13:4xZ)

**Verdict of record: `ENTROPY_NOT_CONFIRMED`.** Computed by the frozen `gate1.py` (written and
tested before the data existed; `coordination/GOAL.md` step 4) from
`local_claude_1/nn-bot/results/entropy-gate-0901/gate1-verdict.json`.

## The question

Does removing the entropy bonus (`entropy_coef` 0.01 → 0) make the self-play-trained clone play
better against the champion's file? Two arms from the same clone, same seed 41, same everything
— verified from the retrieved run configs to differ in exactly one field — trained on the
cluster to 2,709 updates each: **E00** (entropy 0, the treatment) and **E01** (entropy 0.01, the
control). The gate reads benched argmax play on fixed panels, never training numbers.

## The numbers

**Confirmation panel — 144 cells (72 maps × 2 seats), the same cells for both arms and both
ages; 0 illegal commands, timeouts or referee errors:**

| update | E00 (entropy 0) wins / 144 | E01 (entropy 0.01) wins / 144 | paired effect E00 − E01 per cell |
|---|---|---|---|
| 1,500 | 24 (seat 0: 15, seat 1: 9) | 23 (12, 11) | +0.007 |
| 2,500 | 21 (12, 9) | 22 (12, 10) | −0.007 |
| **mean over the two ages** | | | **0.000, 95 % interval [−0.017, +0.021]** (10,000 clustered bootstrap draws over the 144 units, both ages carried together) |

- The interval contains zero → **NOT CONFIRMED** by the frozen rule (CONFIRMED needs the whole
  interval above zero *and* a positive effect at each age *and* clone non-inferiority).
- Effect positive at each age: **no** (+ at 1,500, − at 2,500).
- Clone non-inferiority of the treatment arm: **holds** — the clone (26 of 144 on the same
  panel) wins 3 cells E00 loses and E00 wins 3 cells the clone loses; net 0 of the 6 allowed.
- Margin, not the gate: E00 − E01 = −1.6 points per cell, interval [−4.7, +1.2].

**Scouts — 48 cells, five ages** (a ±5-win look, not a verdict): E00 10 / 12 / 9 / 6 / 7,
E01 8 / 6 / 10 / 6 / 8 at updates 500 / 1,000 / 1,500 / 2,000 / 2,500; paired +2 / +6 / −1 / 0 / −1.

**Training side** (`entropy_log_read.py`, the full 2,709 shared updates, 11 blocks): the bonus
raises entropy by +0.068 [0.051, 0.083] — the knob works — and changes nothing else: win rate
+0.004 [−0.004, +0.011], referee margin −0.02 [−0.56, +0.52]. The host pair (same design, this
machine) replicates it at its 1,753 shared updates.

## What it means, in plain words

The entropy bonus was the prime suspect for the drift of the staged runs (chatgpt_1's second
opinion, 08-31). It is acquitted: with it or without it, the arms are the same bot to within the
gate's resolution, on the training side, on the scouts and on the locked panel. And both arms
show the shape every run has shown — the scout falls from 12 to 7 wins between updates 1,000
and 2,500 — so whatever drives the decay with depth, it is not entropy.

The credit-path measurement of the same day points elsewhere: the plan head learns from a
signal that is 97.7 % the critic's own values and 2.3 % observed reward, because wood's whole
payoff arrives on the final turn and the trainer looks ahead ~8–10 turns. The next lever is
the reward path, not entropy — the fix menu awaiting the owner's choice: slide wood's payoff
into the turns that earn it (`wood_shaping + end_wood = 4`, e.g. `2 + 2`), then longer rollouts,
then whole-game returns, then the critic.

## Identity and reproduction

- Arms: `ppo-yt-e00b` / `ppo-yt-e01b` on the cluster (retrieved archives sha256 `175c656e…` /
  `f33560ba…`), 2,709 updates each in 1.90 h / 1.76 h, no preemption; trainer argument lists
  differ at exactly two positions (`entropy_coef`, the run name); clone `970097ed…`.
- Benches: `bench_ages.py` with identical flags for both arms (`--seed 0 --train-p 0.02
  --both-seats`, argmax network, the champion's file `candidate-champion-denial-off-v6-instrument.rs`
  sha `0e92f8fa…`, `libtroll_farm.so`); panels `smoke-maps-seed0.jsonl` (48) and
  `locked-panel-seed1.jsonl` (144). All fifteen bench files and the verdict JSON are in
  `local_claude_1/nn-bot/results/entropy-gate-0901/`.
- Re-run the verdict: `python3 local_claude_1/nn-bot/gate1.py --treatment 1500=<e00b u1500>
  --treatment 2500=<e00b u2500> --control 1500=<e01b u1500> --control 2500=<e01b u2500>
  --clone <clone locked>` on those files.
