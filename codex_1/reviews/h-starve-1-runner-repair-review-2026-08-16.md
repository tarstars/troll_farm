# H-STARVE-1 runner repair review — 2026-08-16

Verdict: **RUNNER REPAIR AND FOUR REPORTED COUNTS REPRODUCED; CAUSE LABELS REMAIN
UNTRUSTED.**

Reviewed pinned artifact `88114a18019a9607dabf7e2583b188252bdd3ca9` and independently ran
`audit.py OSC-001,OSC-002,OSC-012,OSC-031`. The custom loop now calls
`referee.apply(line)` followed by `referee.grow()`, and all four resident/instrumented command
streams compare identical. The emitted counts and branch mixes reproduce exactly. This accepts
the correction's withdrawal of every pre-repair measurement and its conclusion that the earlier
divergence was a runner artifact.

It does **not** establish three `GENERATOR_GAP` causes. The earlier semantic blockers are still
present:

- `unit_offered_work()` treats geometric reachability to any plant as work, without checking the
  unit's legal `HARVEST`/`CHOP` capability or the plant's actionable state. In particular, the
  previously identified OSC-012 unit has zero harvest and zero chop capability, so a reachable
  plant is not evidence of an eligible action.
- A carrying unit is counted as having work unconditionally, without proving a reachable legal
  bank/plant sink.
- `all_none` is an aggregate candidate count, not direct candidate kinds and chosen-action
  evidence. Exact one-row-per-target-per-window-turn coverage and duplicate rejection are still
  absent.
- The runner still silently accepts early stdout closure with `break`; the requested fail-closed
  behavior and explicit plain/plain plus omitted-grow negative controls are not present.

Therefore the four rows are reproducible **raw packet-lite observations only**. OSC-001,
OSC-012, and OSC-031 must not be promoted to established `GENERATOR_GAP`; the standing causal
state remains zero established causes. Before extending the table, implement a per-unit
eligible-action oracle with positive/negative controls, direct candidate/chosen logging, exact
coverage checks, and fail-closed runner controls.
