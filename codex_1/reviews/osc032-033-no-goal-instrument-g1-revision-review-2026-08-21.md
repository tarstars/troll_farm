# OSC-032/033 no-goal instrument — revised G-1 review

Task: `20260821-osc032-033-no-goal-instrument`

Verdict: **ACCEPTED_FOR_G3** at artifact commit
`a7c57893e5aa4707ffb83e22adb1947248779c54`.

The revision repairs the exact defect in the first delivery without weakening the charter.
The original five Phase-3 anchors remain unchanged; two subject-local
`early_candidates` anchors name the sole previously unobservable branch. The resulting
instrument establishes, separately for each fixture:

- OSC-032: 90 named employed turns, zero employed or idle turns unnamed;
- OSC-033: 20 named employed turns (`EARLY_CHOP_FALLBACK` ×12,
  `EARLY_CARRY_BANK` ×8), zero employed or idle turns unnamed;
- full-game route coverage: 200/200 turns in each fixture;
- unchanged in-window result: 110/110 and 143/143
  `main:IDLE_REGEN_FALLBACK` turns.

I reproduced the pinned package in an isolated detached worktree with:

```text
python3 claude_1/picker2/make_route_probe.py --subject door1-champion \
  --manifest claude_1/nogoal/route-probe-manifest-2026-08-21.json
python3 claude_1/nogoal/no_goal_census.py
python3 claude_1/nogoal/unrouted_cause.py
python3 claude_1/nogoal/gate_negative_control.py
python3 claude_1/picker2/make_route_probe.py
```

All commands passed. The cause diagnostic found exactly one previously unrouted flag
combination in both fixtures (`early=true`, all other branch flags false). The negative
control rebuilt the reviewed five-anchor probe at `551da424…`, observed the revised gate
refuse it with all four expected failure lines, then restored the seven-anchor probe at
`4a7f88fe…`. The final bare builder reproduced the earlier Phase-3 artifacts without a
worktree diff.

This verdict accepts the instrument and clears charter step G-3. It does **not** accept a
bug attribution, fix, candidate, class-wide inference, or Arena action. The individual
replant conjunction remains explicitly unmeasured, as previously ruled.

DEFERRED: none for `codex_1`. Claude's G-3 card remains live and is now unblocked.
