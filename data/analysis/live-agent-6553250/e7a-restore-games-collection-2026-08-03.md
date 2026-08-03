# Exact E7a restore game collection

Date: 2026-08-03

Task: `20260803-collect-e7a-restore-games`

## Outcome

The complete visible finished-game queue for active restore agent `6592131`, submission
`41086057`, was collected and published as a sanitized Git LFS corpus.

- battle rows: 162, all finished, no pending rows;
- exact target identity: 162/162 agent `6592131`, submission `41086057`;
- replay fetches: 162 succeeded, zero failed, zero pre-existing in this isolated checkout;
- canonical raw bytes: 40,902,888;
- cumulative local parser: 452/452 parsed, zero failures;
- cumulative QA: zero unexpected score mismatches and zero tree-invariant violations;
- independent submission-scoped audit: identity clean, zero fetch failures, zero runtime signals.

The three new QA penalty-only rows are opponent-side platform penalties. The target bot's
submission-scoped checkpoint reports zero runtime signals.

## Current mature read

At 2026-08-03T18:04:55Z the active restore had 162 finished games:

- score 23.56, rank 32/137;
- 93 wins, 3 ties, 66 losses;
- mean margin +9.8086;
- 18 catastrophic losses (11.11%);
- negative-margin mass 5,569;
- exact agent/submission identity and zero runtime signals.

This is the second complete mature run of exact E7a. Together with the prior exact deployment's
25.26/160 row, the submission registry now reports two mature runs, median 24.41, worst 23.56,
best 25.26. It is the registry's leading repeated-evidence source, while still below the project's
25.40 goal and not a later confirmation of the earlier 25.26 value.

## Repository package

Directory: `data/shared-lfs/e7a-restore-agent-6592131/`

- replay payload: `games-agent6592131-submission41086057.jsonl.gz`;
- payload bytes: 5,812,614;
- payload SHA-256: `f9567974865fc4c940f6aa4f214758a3cb4e1b9467605dbdb236c8921fffcc23`;
- battle index SHA-256: `b5839f6ce9c6752d7740b7bcf412fc8e0732ec04266d7e6fda1cee77c0d5b21c`;
- manifest SHA-256: `217154fb0310ad7a4cee90b944ac5e4aae1277635b26389ef5598d383b79870d`;
- game-ID interval: 897921883–897928618, with the exact 162 IDs enumerated in the manifest.

The compressed payload contains one complete sanitized replay per JSONL line. The manifest pins
the source and exported SHA-256 for every game. The raw cache remains local and unchanged after
acquisition; the repository copy is an immutable derived mirror.

## Privacy treatment

The export does not copy personal presentation or session fields. Pseudonyms are replaced with
`PLAYER_0` and `PLAYER_1`; `userId`, `avatar`, `publicHandle`, and `testSessionHandle` keys are
removed. Game IDs, agent IDs, and submission IDs remain because they are the technical provenance
keys required to reproduce matchup and version filters. A recursive structural scan over all 162
exported replay rows and battle-index rows passed with no forbidden key.

The deterministic exporter and its regression test are `cgauto/export_agent_replays.py` and
`tests/test_export_agent_replays.py`.
