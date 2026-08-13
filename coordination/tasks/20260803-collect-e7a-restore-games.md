# 20260803-collect-e7a-restore-games: collect active restore replays

- Status: complete — 162 games collected; sanitized LFS corpus remotely verified
- Priority: direct owner assignment
- Owner / worker: local_codex_1
- Created UTC: 2026-08-03T17:57:31Z
- Last updated UTC: 2026-08-03T18:12:32Z
- Agent / submission: `6592131` / `41086057`

## Objective

Fetch every finished battle currently visible for the active exact-E7a restore, store replay
bodies through the repository's canonical immutable `data/raw/games/<gameId>.json` collector,
rebuild and QA the tracked parsed corpus, then commit and push the new data and audit record.

## Safety boundary

- Use `python3 data/scripts/collect.py --agent-id 6592131 --agent-only`; do not run the wide
  top-player collector or touch the 05:17 cron.
- Accept only battle rows for agent `6592131`; record submission identity from replay metadata.
- Preserve existing replay files byte-for-byte; the collector skips existing game IDs.
- Run the canonical cumulative parser and QA after collection; do not hand-edit raw replay JSON.
- No Arena mutation is authorized or in flight.

## Baseline

The isolated worktree contains 290 canonical raw replay files before this collection. The active
restore's battle-list file is absent. Existing unrelated untracked simplification artifacts are
out of scope and will not be staged.

## Result

The public endpoint returned 162 finished rows. All rows carry exact target agent `6592131` and
submission `41086057`; all 162 replay bodies fetched successfully. The isolated cache grew from
290 to 452 files. Canonical cumulative parse and QA pass at 452/452 parsed, zero failures, zero
unexpected score mismatches, and zero tree-invariant violations. A separate submission-scoped
checkpoint is identity-clean with zero runtime signals at score 23.56/rank 32/137.

The 40,902,888 raw bytes are exported as a 5,812,614-byte deterministic sanitized JSONL-gzip LFS
object, SHA `f9567974...`, under `data/shared-lfs/e7a-restore-agent-6592131/`. Names are replaced
with position placeholders and personal/session keys are removed; technical game, agent, and
submission IDs remain. The manifest enumerates every game and source/export hash. The raw cache,
cron, bot source, and Arena state were not otherwise changed.

The submission registry now includes the complete restore row: exact E7a has two mature runs,
median 24.41, worst 23.56, best 25.26. Report:
`data/analysis/live-agent-6553250/e7a-restore-games-collection-2026-08-03.md`.

Remote payload commit `90e8890e` pushed once with `Uploading LFS objects: 100% (1/1), 5.8 MB`.
A fresh standalone clone with smudge disabled first materialized the exact LFS pointer, then a
selective pull reproduced payload SHA `f9567974...` and 5,812,614 bytes. The remote branch and
local head both resolve to `90e8890e21237a9be9fe11c94c658be4d2c60beb` at this checkpoint.
