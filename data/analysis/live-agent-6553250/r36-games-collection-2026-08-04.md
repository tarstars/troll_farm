# Round-36 full replay collection

Date: 2026-08-04

Task: `20260804-collect-r36-games`

## Outcome

All 160 finished games for settled round-36 agent `6594200`, submission `41090606`, were
downloaded through the public read-only game-result endpoint and exported as a sanitized Git LFS
corpus. This operation did not write the collector-owned `data/raw/games/` tree, did not touch its
cron, and did not mutate the Arena.

- battle rows: 160, all finished;
- exact target identity: 160/160 agent `6594200`, submission `41090606`;
- replay fetches: 160 succeeded, zero failed;
- external staging bytes: 40,006,551;
- replay lines: 160, with 160 non-empty frame lists and 86,940 total frames;
- exact game-set equality with the settled checkpoint: 160/160;
- per-replay exported hash verification: pass;
- independent second export: byte-exact package and battle index;
- exporter regression test: pass.

## Repository package

Directory: `data/shared-lfs/r36-agent-6594200/`

- replay payload: `games-agent6594200-submission41090606.jsonl.gz`;
- payload bytes: 5,774,722;
- payload SHA-256: `59f6283beaa10df378335e91d81021bb1a275140266cecf7cdc3a965e8c77549`;
- battle index SHA-256: `340d7ce2b27956d0161de17c701e973b8ab26c179f0a419a7a732aa862c5cb3f`;
- manifest SHA-256: `49a869108bc6433f0fe5c538f1f50fe5a7f48c46c6b97c479dabbe08bb503a72`;
- game-ID interval: 898013296–898015332, with all exact IDs enumerated in the manifest.

Each compressed JSONL row retains the full available replay fields needed for analysis:
`refereeInput`, `scores`, `ranks`, `tooltips`, and `frames`, plus sanitized agent metadata. The
battle index supplies the exact agent, submission, seat, and opponent linkage.

## Privacy treatment

The Git-published export replaces every player name with its positional placeholder
`PLAYER_<position>`. It removes `userId`, `user_id`, `avatar`, `publicHandle`, and
`testSessionHandle` keys. A recursive structural scan over every replay and battle-index row
passed; a separate byte scan found zero source nickname occurrences. Technical game, agent, and
submission IDs remain because they are required to select versions and matchups reproducibly.

## Remote verification

Payload commit `936cf577` uploaded one 5.8 MB LFS object successfully. A fresh standalone clone
with automatic LFS smudging disabled first contained the expected 132-byte, three-line pointer.
The tested selective pull using `--include=<exact path>` then materialized exactly 5,774,722 bytes
at SHA-256 `59f6283beaa10df378335e91d81021bb1a275140266cecf7cdc3a965e8c77549`.
The clone, local checkout, and remote branch all resolved to
`936cf577736573978d1aca92860cb0e46d5433a5` at that verification checkpoint.
