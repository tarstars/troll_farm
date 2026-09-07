# Frozen PLAN — parent-anchored banked-seed BANANA timber cycle

Frozen 2026-09-07 08:20Z, BEFORE any source edit, in reply to the 073752
PRIMARY-REVIEW ("Next independent family: parent-anchored BANANA seed-to-wood
plan using banked stock, without rare fruit acquisition").

Owned (all new): `claude_candidate_seedplan_core.rs`, `claude_candidate_seedplan.py`,
`test_claude_candidate_seedplan.rs`, generated `claude_candidate_seedplan_a*.rs`,
and this run directory. Parent `claude_candidate_policy_flat.rs` (95ee691e) and
every `macroplan`/`dispatch` file are READ-ONLY.

## 1. The one candidate plan (no third worker, no funding)

`Timber { worker, plot, target, opened, phase }`, at most one open per game.
Phases advance ONLY from observed referee state, never from an intended action:

* `Seed`   — the owned worker banks any cargo, walks to its own shack, `PICK w BANANA`
             (one already-banked seed, the only cost), walks to `plot`, `PLANT w BANANA`.
* `Grow`   — a BANANA appears at `plot`: the worker is RELEASED to the unchanged
             parent every turn until `ready_in <= travel + unload`, so growth time
             is real parent production, not idle waiting. Entered only on sight of
             the tree.
* `Fell`   — `tree.size >= target`: unload if `free() < target`, walk to `plot`,
             `CHOP w` until the referee removes the tree.
* `Bank`   — tree gone from `plot` while we were chopping: walk home, `DROP w`.
* `Done`   — wood is in the bank; all protection released.

Yield law taken from the referee, not assumed: felling gives `min(size, free)` wood
at 4 points each; BANANA health is `2 + size`, growth is `+1 size / 6 turns`
(4 near water). `target = clamp(worker.cc, 1, 4)` — capacity-limited, so a cc1
troll fells at size 1 and never waits for wood it cannot carry. No map-specific
schedule or stat tuning.

Cancellation (parent fully restored, protection released): worker gone; plot taken
by a foreign plant before planting; no banked BANANA left and none carried; our
tree destroyed before `Fell`; `turn - opened > 80`; the remaining cycle no longer
fits before turn 300.

Ownership/legality: a worker whose parent command this turn is `PICK`/`PLANT` is
never displaced, so parent memory always describes commands really issued. `TRAIN`
is never removed. Overrides replace (never duplicate) that unit's parent command;
parent `MOVE`s ending on a held cell are shortened along their own target. The only
protected resource is OUR OWN tree at `plot`, and only while the plan is open: a
parent `CHOP` there is REDIRECTED to the nearest unprotected tree, never suppressed.

## 2. Alternatives priced (<= 2 + parent)

Predeclared, not a scan: `plot A` = nearest empty walkable near-shack site
(BFS distance 1..=4 from our shack, no plant, no unit); `plot B` = nearest such
site adjacent to water (BANANA cooldown 6 -> 4). B is skipped when absent.

## 3. Pricing

Three roots (parent, A, B) through the ACTUAL referee, equal horizon 60, mid
checkpoint 30 recorded as a DIAGNOSTIC only (an unfinished cycle is allowed to be
negative at 30). Own-side continuation in every branch is the actual parent leaf
`Policy` clone plus this same state machine on a cloned plan. Window
`30 <= turn <= 140`, so `140 + 60 = 200 < START_TURN = 220`: every simulated
own-side turn is one where the real parent returns exactly its leaf commands, no
nested `SearchBot`. Opponent: the parent's adaptive V439 opponent policy supplies
the identical root turn for all three branches, then ONE identical cheap model
continuation with `contest = true` (the conservative hypothesis: the opponent
prefers trees at OUR door, so it can take our seedling). Accept the best branch
only when `value[60] - parent_value[60] >= 1.0`. Budget 2 evaluations per game,
spacing 25.

## 4. Measured prerequisites, in order (stop at the first failure)

1. Focused tests build and pass under rustc 1.90.
2. Behavioural gate on unmodified known maps 9947500..07 vs the adaptive opponent,
   both seats: same state OFF vs ON, configured (not forced) activation, seed paid,
   PLANT, growth, CHOP, DROP, positive seed-net wood return; negative case included.
3. Only then: source <= 100000 UTF-16, 16 original/pruned/compact equality streams,
   max interactive < 50 ms, then the single 192-pair panel.

No second variant, no post-result tuning. If no real profitable complete cycle is
observed, no panel is run and the named defect is reported instead.
