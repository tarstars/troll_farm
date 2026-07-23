# D61p snapshot collector readiness (2026-07-21)

## Status

The passive current-field acquisition entry point is implemented and locally tested. No network
request, TestSession, Arena comparison, submission, or resident change has been made.

## Frozen implementation

- acquisition protocol SHA-256:
  `0a6e1a49396a7e615d0c190e1e246ce16616b2c0fbf6fb48f9e41648dafc06ec`
- `data/scripts/collect_snapshot.py` SHA-256:
  `1c5894f3c6f76d8568b418a55b871e08cacb428ff4fe47bd9e4f2b15557b6745`
- `tests/test_collect_snapshot.py` SHA-256:
  `1eb79ed064d83b34a32d708cdcfad88b575fdd85dd95ffd0e5fa8f7c1b9ffc12`

The collector:

- creates a new `data/raw/snapshots/<UTC>-d61p/` directory with collision refusal;
- never writes the dirty singleton leaderboard, player, battle, or fetch-log manifests;
- retains every visible resident-`6561795` completed game, ten newest completed games per first 20
  Legend leaderboard rows, and any visibly identified Boss game;
- deduplicates game IDs while retaining all source-agent/rank/cohort provenance;
- records service, request-body hash, response hash, UTC time, source agents, and source ranks;
- enforces at least 0.35 seconds between request starts and a 20-second timeout;
- writes new replay bodies atomically into the shared game-ID cache and never replaces an existing
  body, including race and invalid-cache handling;
- classifies every wanted game as fetched, already present, race-present, or failed; and
- publishes `manifest.json` atomically only after classification is complete.

## Verification

Command:

```bash
.venv/bin/pytest -q tests/test_collect_snapshot.py tests/test_collect.py
```

Result: `11 passed in 0.14s`. Tests cover top-20/resident overlap, outcome-blind recent selection,
Boss retention beyond the ten-game cut, cross-agent deduplication, immutable existing cache,
invalid-cache refusal, snapshot collision refusal, untouched singleton sentinels, request hashes,
minimum pacing, and timeout enforcement. All tests use an injected fake client; they cannot contact
the platform.

## Authorized invocation

After explicit authorization for passive public collection only:

```bash
.venv/bin/python data/scripts/collect_snapshot.py --resident-agent-id 6561795
```

The resulting manifest must be inspected and hashed before parse/QA. This command does not grant or
imply authorization for TestSession, Arena, or submission.
