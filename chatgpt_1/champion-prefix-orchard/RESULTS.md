# Champion-prefix orchard experiment

**Verdict: `DEAD_ON_NORMAL_PAIRED_REPLAY`**

The unchanged champion was the executable in both worlds. The candidate
forwarded its stdout byte-for-byte through the champion's own second
`TRAIN`; only the post-prefix orchard macros could be overridden. Third
training was disabled and `NO_PLANT` was always legal.

## Registered gates

- Prefix byte-identical: **True**
- Second TRAIN unchanged: **True**
- Baseline mechanics clean: **True**
- Globally valid policies: `NO_PLANT, BANANA-s85-k4-d4, BANANA-s100-k4-d4, APPLE-s70-k2-d2`

## Primary result: leave-one-map-out policy choice

- paired final margin: mean **0.0**, 95% bootstrap interval **[0.0, 0.0]**, n=24;
- paired own score: mean **0.0**, 95% bootstrap interval **[0.0, 0.0]**, n=24;
- `NO_PLANT` was the per-map oracle choice on **8/24** maps;
- in-sample global policy: `NO_PLANT`.

The leave-one-map-out number, rather than the per-map oracle upper bound,
is the primary mechanism estimate. All maps are still development data.

## Wood calibration

```json
{
  "aggregate_overstatement": null,
  "p90_overstatement": null,
  "predicted_but_zero_realized_games": 0,
  "predicted_games": 0,
  "predicted_total": 0.0,
  "realized_total": 0
}
```

## Why execution stopped

- paired final-margin lower 95% bound is not above zero

The card requires an immediate stop on any of these conditions, so no
high-raid rerun, panel, holdout, ladder, platform, Arena or cluster work
followed.

## Reproduction

```bash
bash chatgpt_1/champion-prefix-orchard/run.sh
```

Machine-readable rows and every policy summary are in `results/result.json`.
