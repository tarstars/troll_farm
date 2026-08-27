# Fresh telemetry fixture library — first-day cut (2026-08-27)

Task: `20260826-fresh-fixture-dataset` (Track 0-3). This is generated evidence from real
ladder games, not a frozen gate and not a prevalence estimate.

## Input and regeneration

- Deterministic collector slice: 212 games, game-id ascending, archive SHA-256
  `83789b28d3b77410961f7d2ceb81f8254d96a80ccc99a478e010571f9af21ada`.
- Every replay file is checked against the coordinator's manifest before it is decoded.
- Regenerate for a new bot with `scripts/cut_fixtures.py --manifest MANIFEST --games-dir
  GAMES --bot-hash HASH --output LIBRARY.json`; then grade it with
  `scripts/cut_fixtures.py --grade LIBRARY.json`.
- Each fixture records bot hash, game id, replay-derived seat, unit id where applicable,
  event interval, selection rule, and the version-6 telemetry window.

## First library

| class | champion + v6 `72673124…` | keep-rule + v6 `04e3db43…` |
|---|---:|---:|
| dance (`wc>0` or `xc>0`) | 0 | 0 |
| parked troll (10+ consecutive explicit waits while concrete work is available) | 29 | 0 |
| blocked troll (resolver branch `W`) | 139 | 8 |
| stall (60+ consecutive explicit waits while concrete work is available) | 0 | 0 |
| turn-100 shack engine not starting | 0 / unavailable | 0 / unavailable |
| long-kept goal (`ka>30`) | 0 | 0 |

The two generated JSON libraries pass the grading harness with zero integrity errors. Zero
means absent from this deterministic 212-game slice, not absent from the population. The
turn-100 shack-engine class is specifically unavailable: version-6 telemetry does not expose
referee-success ownership or the engine-start predicate, so the generator refuses to infer it
from a proxy. A later instrument must add that field before this class can become evidence.

The blocked-window count is event-window count, not independent-game prevalence: a game may
contain more than one blocked turn. The parked detector coalesces each maximal run.

## Validation

```text
uv run pytest -q tests/test_cut_fixtures.py
2 passed

uv run python scripts/cut_fixtures.py --grade codex_1/fixtures/champion-v6-72673124-2026-08-27.json
PASS

uv run python scripts/cut_fixtures.py --grade codex_1/fixtures/keep-v6-04e3db43-2026-08-27.json
PASS
```

Review requested from `claude_1`, the one reviewer named by the charter.
