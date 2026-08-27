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
| blocked troll (resolver branch `W`) | 45 runs / 139 turn-windows | 4 runs / 8 turn-windows |
| stall (60+ consecutive explicit waits while concrete work is available) | 0 | 0 |
| turn-100 shack engine not starting | 0 / unavailable | 0 / unavailable |
| long-kept goal (`ka>30`) | 0 | 0 |

The champion library covers 208 decoded games and 56,288 telemetry rows; the keep-rule
library is only a **4-game sample** (1,200 rows) and is held as a record until the offered
second disjoint slice lands. Both have zero games without telemetry. The two generated JSON
libraries pass the grading harness with zero integrity errors.

Zero usually means absent from this deterministic slice, not absent from the population.
Two champion-arm labels are stronger: the keep machinery is inactive (`k=0` on every unit-row),
so `long_kept_goal` and the `xc` half of `dance` are inapplicable to that arm. `wc=0` throughout
both arms, so `dance` has no positive control on real input yet. The
turn-100 shack-engine class is specifically unavailable: version-6 telemetry does not expose
referee-success ownership or the engine-start predicate, so the generator refuses to infer it
from a proxy. A later instrument must add that field before this class can become evidence.

Blocked fixtures remain per-turn windows for compatibility, but the table also reports maximal
per-unit runs; adjacent radius-3 windows overlap. The parked detector coalesces each maximal
run. `stall` is a strict subset of the parked detector's output (every 60-turn stall is also a
10-turn parked-troll run), so class counts are not a partition and must not be summed.

Harness consumers should import `decode` from `scripts/cut_fixtures.py`; fixtures intentionally
carry raw version-6 telemetry rather than a second decoded schema.

## Validation

```text
uv run pytest -q tests/test_cut_fixtures.py
3 passed

uv run python scripts/cut_fixtures.py --grade codex_1/fixtures/champion-v6-72673124-2026-08-27.json
PASS

uv run python scripts/cut_fixtures.py --grade codex_1/fixtures/keep-v6-04e3db43-2026-08-27.json
PASS
```

The one chartered review returned ACCEPT-WITH-EDIT. Edits 1–5 were applied. The optional
proposal to strengthen grading against edited libraries was declined because the manifest and
source replay hashes are checked at generation time and no accepted count depends on it.
