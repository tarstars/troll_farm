# 20260804-collect-r36-games: export the settled round-36 replay corpus

- Status: in progress — exact 160-row battle list confirmed; replay fetch starting
- Priority: direct owner assignment
- Owner / worker: local_codex_1
- Created UTC: 2026-08-04T16:34:38Z
- Last updated UTC: 2026-08-04T16:34:38Z
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
