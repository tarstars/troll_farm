# Champion-prefix orchard experiment

**Verdict: `EXECUTION_ERROR`**

The unchanged champion was the executable in both worlds. The candidate
forwarded its stdout byte-for-byte through the champion's own second
`TRAIN`; only the post-prefix orchard macros could be overridden. Third
training was disabled and `NO_PLANT` was always legal.

## Registered gates

- Prefix byte-identical: **None**
- Second TRAIN unchanged: **None**
- Baseline mechanics clean: **None**
- Globally valid policies: ``

## Primary result: leave-one-map-out policy choice

- paired final margin: mean **None**, 95% bootstrap interval **[None, None]**, n=None;
- paired own score: mean **None**, 95% bootstrap interval **[None, None]**, n=None;
- `NO_PLANT` was the per-map oracle choice on **None/None** maps;
- in-sample global policy: `None`.

The leave-one-map-out number, rather than the per-map oracle upper bound,
is the primary mechanism estimate. All maps are still development data.

## Wood calibration

```json
null
```

## Reproduction

```bash
bash chatgpt_1/champion-prefix-orchard/run.sh
```

Machine-readable rows and every policy summary are in `results/result.json`.
