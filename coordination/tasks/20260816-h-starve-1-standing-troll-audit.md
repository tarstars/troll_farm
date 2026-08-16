# 20260816-h-starve-1-standing-troll-audit: why does a troll stand doing nothing for 150+ turns?

- Status: open — OWNER-APPROVED 2026-08-16 as a PARALLEL track ("Yes")
- Code owner: `claude_1` (builds on its own stage-1 re-run machinery) · Reviewer: `codex_1`
  · Integrator: `local_claude_1`
- Priority note: the grader repair (T-1 stage-1 reopen) stays first; this interleaves with
  T-1 fix stages at claude_1's judgment. This is the only score-shaped thread on the board.

## The hypothesis (H-starve-1)

In the long oscillation episodes the real cost is not the dancer but the BLOCKER: a troll
idle (wait fraction ~1.0) for 150–195 turns — half the workforce parked. Suspected cause:
a stuck persistent "regeneration commitment" routes the troll to the ENDGAME candidate
generator mid-game (readable `:1396-1398`); holding no fruit, it gets an empty/WAIT list
every turn and never escapes. If confirmed and fixed, un-parking a worker for ~2/3 of a
game in ~13% of games is real score — unlike the dance fix (+0.045). This is the leading
candidate explanation for the −13.6-below-par mystery (deep-dive deliverable D6).

## The measurement (Packet-lite slice; no cure in this task)

Instrumented build (separate build only; resident byte-exact) over the stage-1
deterministic re-runs of all idle-blocker situations (M1-idle + all M2 + the 4 P4 stalls,
~24 specimens): per turn, for the idle unit, log (a) routing branch taken
(early/main/endgame; commitment flag state), (b) candidate list summary (count, kinds,
chosen), (c) the commitment map. Output: per-situation cause label — e.g.
STUCK_COMMITMENT / NO_WORK_ON_MAP / GENERATOR_GAP / OTHER — with the evidence line.
Grouped cause table goes to the owner session (rulings per cause, not per case — owner
ruling of 2026-08-16). Every new check observed failing first; this doubles as P-1's
candidate-enumeration slice and must be labelled a SLICE, not packet completeness.

## Boundaries

No cure code in this task (the fix, if any, is chartered separately on the audit's
result). No resident mutation, no Arena, no tuning against the prediction registry.
