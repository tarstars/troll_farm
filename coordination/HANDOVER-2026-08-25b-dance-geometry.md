# HANDOVER 2026-08-25b — the dance geometry mission, chartered and delivered in one afternoon

Read `coordination/HANDOVER-2026-08-25-candidate-1-close.md` for everything up to noon (role,
transport, Candidate 1, Arena); this file is the delta since. Written ~15:50Z by `local_claude_1`.

## Resume here

- `coordination/GOAL.md` = **no active mission** (mission archived at
  `coordination/goals/20260825-dance-geometry-measurements.md`). Ritual unchanged:
  `python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`, read whole from the peer's remote
  ref, `--mark` as its own step, commit the seen-state. Every shell command `cd`s into the worktree.
- **Owner's queue (nothing else needs them):** (1) the geometry brief
  `local_claude_1/dance-geometry/owner-brief-2026-08-25.md` → the **Candidate 2 ruling** (swap the
  standing teammate once, or route around it); (2) the Candidate 1 verdict sheet
  `local_claude_1/cure1/owner-verdict-sheet-2026-08-25.md` (park / revise / retire; recommendation
  park); (3) charter the per-troll P4 stall predicate, or leave it recorded.

## What happened 13:30Z → 15:45Z

1. Owner asked what the instrumented real games say about the dance *reason*. My re-read of the
   two reads' published fact rows (`local_claude_1/dance-geometry/re-read-2026-08-25.md`, script +
   results): the teammate stood next to the dance at its start in **55 of 80** and **24 of 25**
   episodes (the accepted r3 labels said 34 / 15 — their blocker test demanded one cell for the
   whole window); all 24 v4 teammate dances carry the mover's letter `R` and never `H`; the short
   "nobody adjacent" dances went 25/80 → 1/25 on the hold arm (p ≈ 0.005, confounded).
2. Owner: *"create goal file for measurements you just mentioned"* → `coordination/GOAL.md`
   mission (M-1 road-around cost with the teammate's cell walled; M-2 what stood on the forward
   cell) → owner ran `/goal` ~13:45Z → task `20260825-dance-geometry-measurements` chartered 13:50Z
   (claude_1 builds, codex_1 definitions first).
3. G-0: r1 14:04Z → codex_1 `REVISION_REQUIRED` (R1–R5) 14:10Z → my construction fact (the hold
   counter is removed on every non-`H` turn, so `R` in an `H`-free window = permanent block) →
   codex_1's objection (holds only where the hold is enabled; 14/160 v4 games scope-disabled → 3 of
   25 episodes) + claude_1's N-1 (first turn uncovered) → **`DEFINITIONS_ACCEPTED` 14:25:09Z**, final
   pin `agent/claude_1@858b5c37` 14:26:49Z.
4. G-1 delivered 14:45:54Z (`agent/claude_1@c5727dc6`); my re-derivation from the rows exact
   (`20260825T145434Z`); **codex_1 fresh-archive reproduction byte-identical** 15:26:53Z
   (`agent/codex_1@28401227`) with rulings: F-1 `NON_COST_BEARING_STATUS` (K-1 191/191 cost-bearing,
   7 `TARGET_OCCUPIED` reported), R1 (`900327649` → `n/a`), K-10 standing, F-3 faithful.
5. **Result:** the standing teammate is on every shortest road on 1,306/1,432 (91 %) and 328/420
   (78 %) measurable turns; the goal is unreachable without its cell on 439 + 55 turns; per dance
   (105): no road 29, +1–2 40, +3–5 15, >5 13, free 7, not measurable 1; `blocked_but_road_exists`
   **0/0**; M-2 on the 25 "nobody" dances: 27 standing / 33 transient / 8 nothing of ours.
6. **Incident:** the VM disk was 100 % full (codex_1's 16 stale fresh-archive extracts, 6.5 GB under
   `/tmp/codex1-*`); codex_1's first reproduction died in `tar` and published nothing for 31
   minutes. Diagnosed via `ssh troll-vm` (launcher wake log + `codex_1.session.log`), cleaned
   15:21:51Z (19 → 13 GB used), rule published `20260825T152239Z` (extracts removed by `trap`;
   `df` before extracting; a dying session publishes a `blocker`). codex_1 accepted and applied it.
7. **Transport:** claude_1's stamps ran +0.3…+13.9 min ahead of their commits in one wake
   (planned round stamps); called (`20260825T143014Z`), conceded, fixed at the cause. Rule:
   stamp and filename from `date -u` in the command that writes the file.

## Arena state — unchanged

Ladder resident: the Candidate 1 instrument (agent `6659743`); champion of record door 1
`547fa706…`, off ladder; `NIGHT-HALT`; no Arena action was taken or authorized this afternoon.

## Owed by me

Nothing to the peers (codex_1's G-1 handoff acked at close). To the owner: the brief is written;
the next charter (Candidate 2 as swap, as route-around, or both as arms) waits on their ruling.
Peer branches still carry ~150+ unmerged commits each; integration owed, non-blocking, pin-only.
