# 20260804-collect-r36-games: export the settled round-36 replay corpus

- Status: in progress — all 160 fetched and locally validated; LFS remote verification pending
- Priority: direct owner assignment
- Owner / worker: local_codex_1
- Created UTC: 2026-08-04T16:34:38Z
- Last updated UTC: 2026-08-04T16:39:43Z
- Agent / submission: `6594200` / `41090606`

## Objective

Fetch every one of the 160 finished replay bodies visible for the settled round-36 agent,
verify exact agent/submission identity and frame completeness, export a deterministic sanitized
corpus through Git LFS, and prove that a fresh cloud-style clone can materialize the full object.

## Safety boundary

- The CodinGame calls are read-only. No submission or Arena mutation is authorized.
- Do not run the wide collector and do not write `data/raw/games/` or any collector-owned file.
- Run the external-storage preflight before bulk writes. Keep private raw responses only beneath
  the verified `data/external/` symlink and publish only the sanitized positional-placeholder
  corpus.
- Require exactly 160 finished rows for agent `6594200`, all with submission `41090606`.
- Preserve game, agent, and submission identifiers needed for analysis; replace player names with
  `PLAYER_<position>` and remove personal/session keys before Git publication.
- Verify the exported game-ID set against the settled checkpoint and verify the Git LFS payload
  hash after a selective pull in a fresh clone.

## Baseline

At start, the public battle endpoint returns exactly 160 finished rows. No corresponding replay
body exists in either local raw cache, and no round-36 shared-LFS corpus exists. The settled
checkpoint is `data/analysis/live-agent-6553250/r36-simplified-settled-checkpoint-2026-08-04.json`.

## Progress

All 160 full replay responses were fetched successfully into `data/external/r36-agent-6594200/`.
The exact settled game-ID set is present, every replay has frames, and the published export has
86,940 frames total. Privacy, per-line hashes, exporter regression, and a byte-exact second export
pass. The 40,006,551 staging bytes produce a 5,774,722-byte package at SHA `59f6283b...`.
