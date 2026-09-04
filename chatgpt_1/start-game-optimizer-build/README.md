# Start-game optimizer build

Task: `20260904-start-game-optimizer-build`.

This directory contains the mechanics-first implementation of the accepted start-game optimizer design. It is generated from the champion of record and adds a parameterised bounded planner whose irreversible branch is `NO_PLANT` versus explicit `PICK -> PLANT` sequences. The tree ledger is finite: each plan pays the seed, planting travel, future felling and banking labour, and measured raid exposure before it receives at most 16 points from one mature tree. The planner never multiplies a production rate by the remaining turns without a tree-mass cap.

The unchanged champion remains the incumbent, fallback and control. The provisional parameter set disables the third-troll branch: the first mechanics candidate is allowed to remain a two-troll orchard bot. `parameters.json` is intentionally separate from the generator so the pending orchard-kinetics read can refit growth, raid and opportunity values without rewriting the search.

## Generated files

- `champion-start-game-optimizer-v6-instrument.rs`: readable diagnostics arm.
- `start-game-optimizer-readable.rs`: readable source derived by the same token transformation.
- `../../cgauto/submissions/candidate-start-game-optimizer-v6-instrument.rs`: compact submission candidate.
- `../../readable/diffs/start-game-optimizer.diff`: owner-readable source diff.
- `../../readable/reports/candidate-start-game-optimizer-v6-instrument.round-trip.json`: lineage and round-trip report.

## Gate order

```text
python3 test_model.py
python3 make_candidate.py
python3 local_claude_1/third-troll/fixtures_diff.py ...
python3 local_claude_1/third-troll/smoke.py ...
python3 claude_1/h2h-panel/turn_time.py ...
```

Value tests are forbidden until both candidate and unchanged champion pass the mechanics gates independently. The 24-map smoke and pinned 200-map panel are development data, not a sealed holdout.

## Scientific boundary

This first candidate is an online bounded policy improver, not a proof of the stochastic turn-300 optimum. `action-manifest.json` states exactly which choices are searched and which remain delegated to the champion. Every emitted command is nevertheless checked by the project’s exact mechanics harness. A later value claim requires the frozen-source fresh holdout specified by the task card.
