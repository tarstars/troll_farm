# D61p historical analyzer stress protocol (2026-07-21)

## Question

Can the newly frozen D61p open-field analyzer reconstruct full-length real official replays at
corpus scale, with exact state, worker, funding, scheduler, and crop-provenance integrity, before
we consume a future current-field snapshot?

This is an infrastructure audit, not a field result. The 1,302 historical games are already
consumed evidence and cannot select a policy, support an attack angle, open confirmation, or
authorize platform activity.

## Frozen corpus and execution

- Consume every row of `data/processed/games.jsonl`, sorted by game ID.
- Require one matching immutable replay at `data/raw/games/<gameId>.json` and one matching command
  stream at `data/processed/trajectories/<gameId>.jsonl` for every row.
- Analyze each game once. Assign the pseudo-resident seat by `gameId mod 2`; analyze the other seat
  as a selected-top source. This balances crop-provenance orientation without inspecting outcomes.
- Preserve all game, map, command, inventory, and score content. Add only the open label needed by
  the analyzer and stable negative analysis-only IDs when a platform agent ID is absent.
- Use a deterministic process pool with 20 workers by default, bounded to 1--32. Record wall time,
  parent-plus-child CPU time, effective cores, and games/second.
- Emit one compact row per game; do not copy full replay states or scheduler traces into the audit
  result.

## Pass gates

All gates are conjunctive:

1. all 1,302 indexed games have raw replay and trajectory files;
2. all 1,302 analysis tasks complete without exception;
3. every command stream has exactly the official number of resolved turns;
4. every official state stream has one more state than resolved turns;
5. there are zero unknown diff updates;
6. every final decoded inventory is exact;
7. every game reconstructs both selected player schedulers;
8. every pseudo-resident crop attribution has zero unknown updates and exact turn alignment;
9. both pseudo-resident seats receive at least 600 games.

Worker/TRAIN agreement, training-event affordability, final scheduler score, and worker assignment
are hard assertions inside the reused analyzer and therefore surface as task failures.

## Interpretation

- **Pass:** the D61p implementation is ready for a current snapshot; proceed only after explicit
  collection authorization.
- **Fail:** repair only the failing reconstruction/integrity mechanism and repeat this exact audit.
  Do not weaken a gate or exclude a replay post hoc.

The measured effective-core count is diagnostic, not a pass gate: decoding includes JSON and disk
I/O, and infrastructure correctness must not depend on host load.

## Invocation

```text
.venv/bin/python cgauto/audit_d61p_analyzer_historical.py \
  --output data/analysis/live-agent-6553250/d61p-historical-analyzer-stress-2026-07-21.json \
  --jobs 20
```

