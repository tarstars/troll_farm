# Oscillation D2 phase-1 viewer rev2 review — 2026-08-16

Verdict: **CODE_ACCEPTED; owner visual acceptance remains pending.**

Reviewed artifact: `e29cf6bd`.  `python3 claude_1/viewer/build_viewer.py --self-test`
passes 23/23.

The rev1 blockers are repaired in code and tests:

- carry slots are parsed in the authoritative subject order
  `PLUM, LEMON, APPLE, BANANA, IRON, WOOD`, with the former wrong order retained as a
  negative control;
- the entry frame is the explicit world state immediately before the first oscillating
  command;
- inferred ordered target is rendered separately from the unit position;
- classification, mechanism, blocker, unresolved facts, and provenance are visible;
- the blocker cell is visibly marked.

I cannot perform the owner's browser/pixel judgment on this host.  That remaining D2
acceptance is deliberately not inferred from HTML-generation tests.

