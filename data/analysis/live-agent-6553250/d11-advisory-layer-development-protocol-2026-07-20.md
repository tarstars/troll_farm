# D11 resident-gated advisory layer — development protocol (2026-07-20)

## Hypothesis

The D11 actor may contain useful immediate-action knowledge even though assigning it a complete
worker role destroys resident coordination.  Preserve every resident route and task by default;
override only when PPO proposes an executable local action while the resident would `MOVE` or
`WAIT`.

This is a nested, conservative follow-up on the same reused development maps.  It cannot promote
a candidate or authorize Arena activity.

## Frozen substrate

- Stable resident controls training, worker specs, and the pre-training trajectory.
- V7 adopts the resident-created worker's exact stats and produces shadow actions.
- Exact runner SHA-256:
  `3547ff337a69c668d66b865c029af11c5581771b88d124bdc71c6d34a49f4515`.
- V7 source/binary SHA-256:
  `9beae086bd92b4d4be4f7a1e2c40042102ed15ff4bd427cf53ad7e249f859f5b` /
  `30d584ee89c6f225039d8e9c3900622745e328760daed0cc597cedc41f0db9d5`.

For every post-training unit decision the runner records exact command agreement, verb
agreement, resident-WAIT/actor-action opportunities, actor-local/resident-transit opportunities,
and actual overrides.

## Policies

| Policy | Override rule after resident training |
|---|---|
| `resident` | never |
| `native_second_idle_only` | PPO controls the trained worker only when resident says `WAIT` |
| `native_second_crop_local` | PPO `PLANT/HARVEST/CHOP` replaces trained-worker `MOVE/WAIT` |
| `native_second_productive_local` | any PPO local productive verb replaces trained-worker `MOVE/WAIT` |
| `native_starter_crop_local` | crop-only rule on the starter |
| `native_all_productive_local` | productive-local rule on both workers |

Productive local verbs are `PLANT`, `HARVEST`, `CHOP`, `DROP`, `MINE`, and `PICK`.  PPO `MOVE`
never replaces resident transit except in the explicit idle-only rule.  Resident commands remain
unchanged before the second worker exists.

The seed-0 resident smoke test establishes three useful controls: starter crop-only was inert;
second idle-only changed 8--11 decisions without changing either paired outcome; second
productive-local changed 3--12 decisions and improved one seat by six points; both-worker local
override was already visibly too broad on one seat.  These are tool-validation observations, not
selection evidence.

## Development block

- Reused seeds 0--7, both seats.
- Frozen six-opponent mechanism panel.
- Six policies in every cell.
- Games: 8 × 2 × 6 × 6 = 576.
- Parallelism: 20 exact independent games.

## Primary analysis

Pair every policy to the resident in the same seed/seat/opponent cell.  Report map-balanced
margin and wood deltas, opponent means, direct-resident mean, worst decile, worker-count parity,
override totals/rates, activated-cell count, and gain conditional on activation.

## Frozen gate and selection

A policy is eligible only if:

1. resident worker count is retained in 96/96 games;
2. at least 10/96 cells activate and total overrides are between 1% and 20% of post-training
   decisions;
3. map-balanced mean margin delta is at least +2;
4. the 95% normal lower bound over eight map deltas is nonnegative;
5. worst opponent mean delta is at least -2;
6. worst-decile cell delta is at least -10;
7. direct-resident-opponent mean delta is nonnegative;
8. activated cells have positive mean delta.

Select the eligible policy with the highest map-balanced mean.  Policies within one point are
ordered by fewer total overrides, then by the nested safety order: second idle-only, second crop
local, second productive local, starter crop local, both-worker productive local.

If none passes, close inference-time D11 integration.  The next PPO work must change the training
distribution and objective—resident states, resident intent/assignments, and full-game reward—
rather than add another hand-written activation rule.

## Outputs

- rows: `d11-advisory-layer-development-seeds0-7.tsv`;
- analysis: `d11-advisory-layer-development-2026-07-20.json`;
- result: `d11-advisory-layer-development-result-2026-07-20.md`.

