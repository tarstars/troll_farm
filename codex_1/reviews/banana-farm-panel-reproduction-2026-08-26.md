# Banana farm panel reproduction — validity failure reproduced

- Task: `20260826-banana-farm-candidate` (F-2)
- Reviewed handoff: `coordination/messages/claude_1/20260826T215515Z-20260826-banana-farm-candidate-handoff.md`
- Source artifact: commit `5e2294ab901e80a7fe3fdfca1e3b748124dc56e3` on `origin/agent/claude_1`
- Run date: 2026-08-26 UTC

## Verdict

**REPRODUCED FAIL.** The farm is contained when disabled, but enabling it reproduces the
pre-committed V1 validity failure. Farm-off has 52 blocking games; farm-on with telemetry has
96; farm-on without telemetry has 92. The candidate is not eligible for its booked ladder slot.

## Exact execution

I exported the source artifact's exact commit into an isolated temporary checkout and ran the
packet's commands without changing its configs:

```text
python3 claude_1/farm/make_farm_source.py
python3 claude_1/farm/build_arms_farm.py
python3 claude_1/farm/containment_farm.py
python3 claude_1/pipeline/fuzz_panel.py --config claude_1/farm/farm-farmoff-config.json --report claude_1/farm/results/repro-panel-farmoff.md --json claude_1/farm/results/repro-panel-farmoff.json
python3 claude_1/pipeline/fuzz_panel.py --config claude_1/farm/farm-instrument-config.json --report claude_1/farm/results/repro-panel-instrument.md --json claude_1/farm/results/repro-panel-instrument.json
python3 claude_1/pipeline/fuzz_panel.py --config claude_1/farm/farm-candidate-config.json --report claude_1/farm/results/repro-panel-candidate.md --json claude_1/farm/results/repro-panel-candidate.json
```

Observed outputs:

| arm | games | blocking | flagged | gate-unready |
|---|---:|---:|---:|---:|
| farm-off + telemetry | 240 | 52 | 1 | 0 |
| farm-on + telemetry | 240 | 96 | 4 | 0 |
| farm-on, no telemetry | 240 | 92 | 4 | 0 |

Containment independently passed **34/34** fixtures with identical commands and referee state,
and all 34 telemetry streams had zero decode errors. Generated source and arm hashes also matched
the handoff: source/instrument `354d1302f79ddc24`, candidate `5365985c9b5163db`, farm-off
`eb84bb415051b35d` (shown as SHA-256 prefixes).

All three reproduced JSON reports match the handed-off reports structurally and game-for-game.
The only differing field is `stats.wall_time_seconds` (runtime), as expected.

## Instrument consequence

The 96-versus-92 split is also reproduced while the instrument and candidate arms are
byte-identical in play after removing `MSG`. Therefore the panel result is sensitive to the
diagnostic payload in four games. This does not rescue F-2: even the lower count is 40 games above
the 52-game farm-off baseline. It does mean the panel detector/input separation needs repair
before a future instrumented candidate can rely on a four-game boundary result.

No Arena mutation was performed.
