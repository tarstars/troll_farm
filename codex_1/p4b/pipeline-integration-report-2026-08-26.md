# P4b pipeline integration — v4/v5/v6 narrator parameter

Task: `20260826-p4b-narrator-param` (D-2 integration last mile).

## Result

`claude_1/pipeline/p4b_gate.py` now retains the row-taking `evaluate_rows` API used by
`fuzz_panel.py`, while accepting an explicit narrator module and dialect. The panel exposes
`--p4b-dialect v4|v5|v6|none`; its default remains v4. `none` reports `NOT_APPLICABLE` and fails
closed if any NARRATE payload is present.

## Differential gate

- Unit tests: `python3 -m unittest claude_1/pipeline/test_p4b_gate.py` — 10 passed.
- Accepted standalone tests: `python3 -m unittest codex_1/p4b/test_p4b_gate.py` — 11 passed.
- Candidate 3 v6 instrument archive (`/tmp/claude-1000/cure3/instrument/games/games.jsonl.gz`):
  240 games, `READY`, 0 decoder errors, 15 parked-unit episodes on 15 units.
- Candidate 2 v5 regenerated archives (`/tmp/codex1-p4b-v5-repro/`): the instrument and rule-off
  count projections both match `claude_1/cure2/results/c12-idle-with-work.json` exactly (status,
  games, totals, failed-unit count, blind-population counts, longest-run distribution, tripwire).

No candidate, champion, resident, resolver, Arena state, raw game corpus, or cron was changed.
