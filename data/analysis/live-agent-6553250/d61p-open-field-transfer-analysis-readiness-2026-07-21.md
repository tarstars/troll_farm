# D61p open field-transfer analysis readiness (2026-07-21)

## Verdict

The offline D61p analysis stage is ready.  No platform request was made and no snapshot currently
exists under `data/raw/snapshots`, so there is deliberately no field result yet.

The implementation consumes only a passed snapshot's open game list and its named raw replays. It
does not enumerate or read `processed/sealed_confirmation`. It verifies the exact frozen QA gate
set, source and product manifests, open table, open trajectories, acquisition hashes, and raw
replay hashes before analyzing anything.

## Implemented analysis

`cgauto/analyze_d61p_field_snapshot.py` reconstructs exact official state streams and successful
worker creation for resident and selected top-20 appearances.  It measures training timing and
cost, first affordability, useful funding contributors, worker phase actions and productive
transitions, hybrid/multi-role labor, late renewable loops, resident loss concentration, and
opponent-crop provenance.

The report evaluates the ten attack angles frozen in the protocol:

1. catastrophic-tail control;
2. workforce capitalization;
3. front-loaded scale;
4. coordinated later funding;
5. hybrid/multi-role labor;
6. late renewable loops;
7. opponent-crop compounding;
8. the resident zero-crop tail as a descriptive measure only;
9. TRAIN timing delay;
10. worker utilization.

Supported directions are ordered by the protocol's fixed resident-loss/causal-proximity order, not
by a fitted score.  The report can select only a new offline mechanism protocol. It cannot open
confirmation, construct a candidate, or authorize Arena/submission.

The eventual CPU-heavy replay reconstruction uses a deterministic process pool with up to 20
workers by default (`--jobs`, bounded to 1--32). Irrelevant opponent sides are not scheduled for
worker-policy reconstruction.

## Verification

The focused collector/parser/analyzer/QA/conformance suite reports:

```text
28 passed in 0.22s
```

New coverage includes:

- successful exact resident and selected-top reconstruction from a raw open replay;
- an open loader that succeeds without any sealed-confirmation directory;
- a collector -> parser -> two-process analyzer integration run;
- the semantic boundary that a field zero-crop row stays descriptive while repeated catastrophic
  and crop-compounding evidence may support their own separately defined attack angles.

Frozen file hashes:

```text
e181bc9d43021eed988f897e3e0bf58b61a54ababf4acfb7b1e694edf2a6c617  d61p-open-field-transfer-analysis-protocol-2026-07-21.md
e9ed056c7d5ba1595bc52a563a917d785807219788c8473901d3ee8e242b71df  cgauto/analyze_d61p_field_snapshot.py
2a2a45f5ac9c262e24f7cc1f236ac47e449c2c6cb436aaee9c2ec65deaeaede8  tests/test_analyze_d61p_field_snapshot.py
1c5894f3c6f76d8568b418a55b871e08cacb428ff4fe47bd9e4f2b15557b6745  data/scripts/collect_snapshot.py
a68f8f26ba9dc0a897909e2b4053dee30ceb643d61d20bd3a6ad98def38fa641  data/scripts/parse_snapshot.py
```

## Invocation after authorization and passed QA

Collection remains a separate explicitly authorized step.  After collection and parsing:

```text
.venv/bin/python cgauto/analyze_d61p_field_snapshot.py \
  data/raw/snapshots/<snapshot-id> \
  --output data/analysis/live-agent-6553250/d61p-field-transfer-<snapshot-id>.json
```

The analyzer refuses a failed or changed QA gate set and refuses to overwrite an existing report.

