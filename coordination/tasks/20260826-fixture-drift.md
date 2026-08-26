# 20260826-fixture-drift: Track 0-1 — 23 of the 34 frozen fixtures are `NOT_REPRODUCIBLE_ON_BASE` and silently skipped

- Status: **CLOSED 2026-08-26T15:45Z — the 34 are RETIRED as gates by owner ruling** ("retire old data, build fresh"); files stay as history; successor = `20260826-fresh-fixture-dataset.md`. Diagnosis (subagent, 15:15Z): nothing rotted; the 34 were recorded from the very-old bot `98628e98` and 23 fail only because the champion is a different bot; containment checks all 34; grading was 11/34 and said so. Original status: **OPEN — CHARTERED 2026-08-26T15:05Z by owner ruling** ("you can even start a subagent
  for this task"; "before banana farm build"). Board row 0-1.
- Record owner: local_claude_1 · Work owner: **local_claude_1 via a local subagent** (diagnosis
  phase, started 15:05Z), then whoever the diagnosis names for execution (codex_1 by default —
  it owns the other instrument and reproduces every panel) · Reviewer: codex_1 (one round) ·
  Arena: nothing.
- **Done means:** every one of the 34 fixtures either **runs on the current engine** or has a
  **written retirement line** (the bug it pinned is gone or covered by a named test); the
  harness's summary reports *skipped* fixtures as a count in its own words, never folded into
  "pass"; the next panel verdict states "N of 34 run". Deliverable:
  `local_claude_1/fixtures/fixture-drift-2026-08-2x.md` (diagnosis table + per-fixture decision)
  and the executed changes on `main`.
- **Dead means:** the fixture library cannot be located or replayed at all (then the 34 are
  retired as a set, with that reason, and a fresh library is a new charter).
- **Budget:** diagnosis 1 subagent run (today); execution ≤ 1 day; 0 ladder; 0 bot-source changes.
  **Sequenced before Track F-2's panel** (the farm must not be graded on 11 of 34).
- Created UTC: 2026-08-26T15:05:00Z · Last updated UTC: 2026-08-26T15:05:00Z

## THE QUESTION (owner's, plain words)

The behaviour tests are 34 saved game positions with the move the bot must make there. The engine
we replay them with has moved on, and 23 of the 34 positions can no longer be reproduced on it —
so the harness skips them, for every candidate, on every run, while the verdict still says
"34/34". Two-thirds of the behaviour tests are silently off. Fix that: re-freeze what can be
re-frozen, retire what is obsolete with a line saying why, and make the harness say out loud how
many it actually ran.

## Steps

1. **Diagnosis (subagent, read-only):** where the fixtures live; what "reproducible on base"
   compares; per fixture, the exact reason it fails; recommendation RE-FREEZE / RETIRE /
   REPAIR-HARNESS; effort estimate. → the deliverable's table.
2. **Execution:** apply the recommendations; harness summary line fixed; run the 34 on the
   champion and on the Candidate 3 arm as a check that verdicts do not silently change.
3. **Gate 0-1-G1 (codex_1, one round):** the 34 run or are retired; the summary counts skips;
   the champion's fixture verdict is unchanged in substance.

## Do not touch

Bot sources; the arms; the Arena; `data/raw/games/`; formatters over hash-locked files.
