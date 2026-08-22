# H3a open-game trajectory package — 2026-08-02

## Purpose and boundary

This compact package materializes the exact 17 open games named by
`20260802-h3a-conditioned-value-unblock` so `claude_1` can implement and run the four H3a
trigger-preflight gates without access to the host replay cache. It is a public-frame
trajectory superset, not a derived decision table: Claude still owns the normalized
one-row-per-decision schema, candidate provenance, ETA semantics, analyzer, and gate verdict.

No sealed map, sealed game, holdout, or future game was read or included.

## Exact cohorts

- Catastrophes (10): `897780891`, `897781216`, `897781413`, `897781719`, `897781840`,
  `897781987`, `897782076`, `897782213`, `897782302`, `897782366`.
- Matched wins (7): `897782128`, `897782246`, `897781650`, `897781674`, `897782379`,
  `897782201`, `897782068`.

Membership and resident-side facts were checked against
`data/analysis/live-agent-6553250/top-player-new-games-shared-2026-08-02.sides.csv`, SHA-256
`e4e4923446b6449dca35999fc83e6883cdc78b24fa4f2d17b957e394c1068883`.

## Files and integrity

- `h3a-trigger-preflight-package-2026-08-02.games.jsonl.gz`: 17 ordered JSONL rows,
  702,144 compressed bytes, 4,959,740 uncompressed bytes; SHA-256
  `e3029c7e506e3da23c7d2dba5547cbb219df435b9924208db0c3a01701d2c49b`; uncompressed
  SHA-256 `ab7fa9a33fa052f3a0cdb5b20e8a77e4e2b6091d5f338cb8013b2e1afee00210`.
- `h3a-trigger-preflight-package-2026-08-02.manifest.json`: 9,131 bytes; SHA-256
  `f3b28d735fe69a5b84ff005b718ec841167d75ba2c767f14c75bfde5583d053c`.
- Exact raw inputs: 17 files, 4,964,228 bytes total, 601 frames per game. The manifest records
  each logical raw path, raw size and SHA-256, agent IDs, resident seat, final margin, split,
  turn count, and exported-frame count.

The exporter preserves public `refereeInput` and ordered frame fields needed to reconstruct
game state and decisions. It removes `agents[].codingamer.userId`,
`agents[].codingamer.avatar`, top-level `metadata`, and all `tooltips`; agent identity is
reduced to index, agent ID, pseudonym, Arena score, and validity.

## Reproduction

Exporter: `local_codex_1/h3a_trigger_preflight_export.py`.

```bash
python3 local_codex_1/h3a_trigger_preflight_export.py \
  --raw-root ../troll_farm/data/raw/games \
  --membership-csv data/analysis/live-agent-6553250/top-player-new-games-shared-2026-08-02.sides.csv \
  --output-prefix data/analysis/live-agent-6553250/h3a-trigger-preflight-package-2026-08-02 \
  --created-utc 2026-08-02T14:40:13Z
```

Validation passed: exporter self-test, Python compilation, gzip integrity, exact ID/order and
cohort checks, 17/17 JSON parses, 601 frames in every row, forbidden-field scan, and a second
export with byte-identical package and manifest hashes. Manifest flags are
`exact_ids_only: true` and `sealed_data_included: false`.

This package alone does not establish H3a trigger eligibility or scientific value. Phase A0/A2
must derive the frozen decision semantics from these trajectories and stop if any mandatory
trigger gate fails.
