# Gate verdict — the reward path works (2026-09-01 20:5xZ)

**Verdict of record: the treatment effect is CONFIRMED by the frozen gate** — the interval wholly
above zero, positive at each age, clone non-inferiority held. (The gate program prints the
outcome as `ENTROPY_CONFIRMED` because its four outcome names were frozen for the entropy test;
the decision rule it applies is variable-agnostic and is printed with the verdict. A follow-up
may rename the outcomes; the rule itself was not touched.)

## The question

Does paying half of wood's value on the turn of delivery — `wood_shaping 2 + end_wood 2`, value
preserved at 4 — make the self-play-trained clone play better against the champion's file than
the lump-sum reward (`0 + 4`) every previous run used? Treatment **r22**, control **E01**
(entropy 0.01, `0 + 4`): same clone, same seed 41, same everything; the retrieved configs differ
at the two wood flags and the run name; the payloads are byte-identical by manifest.

## The numbers (locked 144-cell panel, the same cells for every number; 0 faults anywhere)

| update | r22 (wood 2 + 2) | control E01 (0 + 4) | the clone |
|---|---|---|---|
| 1,500 | **31 of 144** (19 + 12; score 138.9 vs 191.5) | 23 of 144 | 26 of 144 |
| 2,500 | **29 of 144** (15 + 14; score 133.8 vs 189.1) | 22 of 144 | 26 of 144 |

- Paired effect r22 − E01 per cell: **+0.052, 95 % interval [+0.003, +0.101]** (10,000 clustered
  bootstrap draws over the 144 map-seat units, both ages carried together). Wholly above zero.
- Positive at each age: **yes** (+0.056 and +0.049).
- Clone non-inferiority: **holds with room** — r22 loses 2 cells the clone won and wins 13 the
  clone lost: **net +11 cells**. r22 at update 1,500 is the first artefact of the programme to
  stand above the clone on the locked panel (31 > 26).
- Margin (not the gate): **+8.3 points per cell, [3.4, 13.6]**.
- The scouts (48 cells: 9 / 7 / 7 / 5→9 vs 8 / 6 / 10 / 6 / 8) barely see any of this — the
  ±5-win lesson, again: the locked panel is where the verdict lives.

## Reproducibility notes

- The cluster training is **deterministic**: the restarted r22 reproduced the preempted attempt's
  scout scores to the decimal at updates 500 and 1,000 (9/136.4, 7/130.5).
- Arm: `ppo-yt-r22`, operation `907fc1d9…` (preempted once at ~update 2,316; the restart ran to
  2,709 and is the run of record), retrieved archive sha256 `e0528d8f…`.
- Benches: `bench_ages.py`, identical flags to every other arm; the verdict JSON and all bench
  files: `local_claude_1/nn-bot/results/entropy-gate-0901/` (`gate1-verdict-r22.json`).
- Corroboration, independent of any critic: claude_1's pricing — the reward enters 40 of 40
  updates under `2 + 2` against 23 of 40 under `0 + 4` (share 1.45 % → 5.34 %); and the offline
  replay (reward rows = endings exactly under `0 + 4`, three seeds).

## What it means, and what it does not

The first positive result of the recovery programme: the reward's shape was starving the
planner, and paying part of wood's value when it is earned recovers real benched strength —
+8 wins of 144 over the control and above the clone for the first time. It does **not** yet mean
a candidate: parity with the champion needs 72 of 144, and r22 stands at 31. Still open in the
reviewer's order, one variable each: the longer rollout (`ppo-host-l128`, training now), the
environment's default split `0.5 + 3.5` (same coverage as `2 + 2`, smaller immediate signal —
worth one arm to know whether the magnitude matters), whole-game returns, value-trunk
separation. The host replication of this very pair (`ppo-host-r22` vs `ppo-host-h01`) lands
tonight and is read by the same gate.
