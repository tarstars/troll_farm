# Champion-prefix orchard oracle

Task: `20260904-champion-prefix-orchard`

This is the narrow offline experiment requested after the first PLANT-aware
optimizer failed.

The executable in both worlds is the unchanged champion.  The candidate
forwards the champion's command line byte-for-byte through the champion's own
second `TRAIN`.  Beginning on the following turn, a bounded external
controller may override one planter and one feller while the same champion
process continues to consume the resulting live states.  That process is the
shadow champion.  There is no custom second-troll prelude, no restart at
hand-back, and no third troll.

The search includes `NO_PLANT`.  It enumerates the published policy grid in
`policies.json`, runs exact paired referee games on the frozen 24-map
development slice, and reports:

- prefix and second-training identity;
- mechanics and new inactivity alarms;
- every fixed policy's paired result;
- an in-sample global best (descriptive);
- a leave-one-map-out global-policy estimate (primary);
- a per-map oracle upper bound and how often it selects `NO_PLANT`;
- explicit predicted versus realised orchard wood;
- a frozen-policy high-raid rerun, but only if no earlier dead condition fires.

The controller plans a **small near reserve**, not a thirty-tree stockpile.
It plants only after the normal champion second troll exists, prefers bananas
for wood, leaves the champion in charge while crops grow, and fells around
maturity.  Each override has an observable one-turn progress condition;
three consecutive misses cause one-way hand-back.

## Run

```bash
bash chatgpt_1/champion-prefix-orchard/run.sh
```

The command writes `results/result.json` and `RESULTS.md`.  A dead condition
is a scientific result and exits successfully after publishing the evidence;
an execution/instrument error exits non-zero.

This directory performs no ladder, platform, Arena, cluster, champion, or
`main` action.
