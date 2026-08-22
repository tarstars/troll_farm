# Oscillation attack on `readable__no_orchard` — independent answer (`claude_1`)

- Task record: `coordination/tasks/20260809-oscillation-attack.md` (authoritative)
- Governing objective: the owner's restatement carried by
  `coordination/messages/local_claude_1/20260809T093000Z-20260809-oscillation-attack-correction.md`
  — *"Oscillations are our lack of control over the program. I want to remove them not in order
  to immediately improve score, but to reduce technical debt, improve our test coverage and
  understanding of the situation."*
- Scope: **analysis and proposal only.** No bot, candidate, parent, `.min.rs`, detector, gate,
  `rust/**`, host, Arena or CI artefact was modified. The only executions were read-only runs of
  the committed panel and of scratch-only replay scripts under
  `/tmp/.../scratchpad/osc/`.
- Author: `claude_1`, 2026-08-09.

## Independence

I did **not** read `chatgpt_1`'s answer
(`coordination/messages/chatgpt_1/20260809T112000Z-...-oscillation-attack-handoff.md`, or
anything on `origin/agent/chatgpt_1`) — skipped per instruction. I also did not read
`local_claude_1/oscillation-attack-local_claude_1-2026-08-09.md` or its amendment, on the same
independence principle, although only `chatgpt_1`'s was named. I read the task record, the
policy, and the correction, which are directives rather than answers.

---

## 0. Provenance — every input, and how to reproduce

Repository `/home/tarstars/prj/troll_farm-claude_1`, branch
`agent/claude_1-banana-restoration-r2` at `346eeae7`; `origin/main` at `a2719070`.

| input | SHA-256 |
|---|---|
| `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (from `origin/main`) | `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29` |
| `claude_1/pipeline/fuzz_panel.py` | `ab2d3b29de83aeaace03efaf8318d4aa9d9c18a090157db634117067f349823e` |
| `claude_1/banana-restoration-r2/trace_detectors.py` | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `claude_1/banana-restoration-r2/regression_tests.py` | `fbd6e8da451522bf0e8ec06826c48912b4d0f1c79961d49023276ba7837f11a1` |
| `claude_1/banana-restoration-r2/semantic_harness.py` | `a471a3c76d2e9d16fd2d2b6896e7a2de50c2e22cc0388d68ba506b25407a77de` |
| `claude_1/banana-restoration-r2/make_banana_traces.py` | `daf9996b2fa40d4a0f5b16dfc7bfd3c9d75c372d4c5761dac4327ce42e3f33d5` |
| `rust/src/botmain/motion.rs` (Gold-era, read only) | `9a3d000d50354814d727a5e389ba15ca0e86ac01832b9480e126ed101335b8f1` |
| `local_claude_1/verification/readable-no-orchard-oscillation-2026-08-08.json` (prior corpus) | `b42fb8a7ae2c26af7e52dd18128a04bf221a794fbffe52e63d57b47122332e69` |
| my panel config (scratch) | `b124a6a3e738cae2a01788bf004e3ccc75df4bffec3dd8205a54e4213e2f08d4` |
| my panel result (scratch) | `9deefa841592fcba1d02d1a8ed93702de24f25d1fc64b893697f22afbb5e08b5` |
| instrumented scratch build source `readable_dbg.rs` | `201781eec670fceb82e499cfcc16060758e22f55310db4925481af3db925d2f9` |

Toolchain: `rustc 1.97.1 (8bab26f4f 2026-07-14)` at `~/.cargo/bin/rustc`; Python 3.12.

**E1 — the corpus rerun (MEASURED).** Config declares
`instrument_version=fuzz-panel/2-train`, `corpus_version=c2-train-2026-08-09`, candidate =
parent = `readable.rs` (`98628e98`), seeds `[982451653, 15485863, 32452843, 49979687, 67867967,
86028121]`, 120 maps × 2 seats, 200 turns, default class/opponent mix.

```
PATH=~/.cargo/bin:$PATH python3 claude_1/pipeline/fuzz_panel.py \
  --config  <scratch>/osc-config.json \
  --report  <scratch>/osc-report.md \
  --json    <scratch>/osc-result.json
# -> BLOCK (240 games, 118 blocking, 0 flagged, 15.1 s)
```

**E2 — the instrumented build.** `readable_dbg.rs` is a scratch copy of `98628e98` with two
`eprintln!` statements added inside
`resolve_move_conflicts_with_priority_and_forbidden` (readable lines 756 and 769) logging
`turn, unit id, current cell, GOAL cell, landing, branch, detour pick, reserved, occupied`.
It adds no control flow. **Control:** the per-turn state and command streams of `bot-dbg` and
the unmodified `bot-98628e98dce4a33b` were compared on eight games (m110/m085/m040/m003 × both
seats) and were **byte-identical** in all eight. Every "goal" and "branch" figure below is
therefore a property of the shipped program, not of an altered one.

**E3/E4/E5 — scratch analysis scripts** (`replay.py`, `analyze.py`, `classify.py`,
`invariant.py`) drive the committed `fuzz_panel.build_skeleton` / `make_referee` /
`regression_tests.run_binary_custom` / `trace_detectors.build_trace` unchanged. They are scratch
only and deliberately not committed; every number they produce is restated here in full.

### Corpus-version caveat (MEASURED)

The committed corpus `readable-no-orchard-oscillation-2026-08-08.json` was produced by the
**pre-repair** referee, in which `TRAIN` and `MINE` were silently discarded. Under the repaired
referee (`fuzz-panel/2-train`) the same candidate on the same seeds gives:

| | prior corpus (`b42fb8a7`) | this rerun (`9deefa84`) |
|---|---|---|
| D-1 episodes | 34 | **35** |
| games with a D-1 episode | 32 | **33** |
| median episode length | 124.5 | 94 |
| worst episode | **194** turns (m110 s1, unit 0) | **194** turns (m110 s1, unit 0) |
| episodes ≥ 62 turns ("terminal mode") | 20 | **20** |
| other detectors | D-4 6, D-5 1, D-6 14, D-9 196 | identical |

The single new episode is **`m040` seat 1, unit 0, turns 80–86, cells (4,0)↔(3,0)** — the
two-worker case the one-worker fiction was masking. Everything else reproduces exactly. The
**terminal mode is unchanged at 20 episodes**; the acceptance test in the task record therefore
still means the same 20 things.

---

## 1. The mechanism

### 1.1 What the mover actually is (MEASURED, from source)

All line numbers are in the readable candidate `98628e98`.

- `bfs_distances` (147–166) and `next_cell` (167–187) run over `GameState.walkable`, which is
  **static terrain cloned from the parsed map** (62, 289). **No unit — ours or the opponent's —
  is ever an obstacle for path computation.**
- The only conflict resolution is `resolve_move_conflicts_with_priority_and_forbidden`
  (726–778). The shipped entry point (`YamoBot::commands`, 1433) calls it through
  `resolve_move_conflicts` (720–722), i.e. with `priority_ids = {}` **and**
  `forbidden_for_non_priority = {}`. Everything about priorities and forbidden cells is dead
  code in the shipped configuration.
- `occupied_now` (736) = the cells of **all own units, including the unit being resolved**.
- `reserved` (737) = the cells of own units that are **not moving this turn** — i.e. parked
  units.
- Direct branch (756–760): if the landing is not reserved, move there.
- Detour branch (762–768): otherwise pick the orthogonal neighbour of the **current** cell that
  is walkable, not reserved, not in `occupied_now`, minimising `(bfs_distance_to_goal, cell)`.

Two consequences follow from the code alone, and I state them as theorems because they decide
which fixes can possibly work.

**Theorem 1 (the direct branch cannot oscillate).** For a *fixed* goal `T`, `next_cell` returns
`argmin (d_T(c), c)` over the cells reachable within `speed` steps, and that set **contains the
current cell** (its own BFS distance is 0 ≤ speed, line 186). If from `X` it selects `Y ≠ X`
then `(d_T(Y), Y) < (d_T(X), X)`; BFS distance is symmetric, so `X` is in `Y`'s candidate set,
and selecting `X` from `Y` would need `(d_T(X), X) < (d_T(Y), Y)`. Contradiction. **A two-cell
alternation with a constant goal is impossible unless the detour branch fires.**

**Theorem 2 (the detour branch fires only against a parked own unit).** The detour branch is
guarded by `landing_forbidden || reserved.contains(&landing)`; with `forbidden = {}` in the
shipped path, only `reserved` can trigger it, and `reserved` contains exactly the cells of own
units that are not moving. **Therefore: with fewer than two own units on the board, D-1 is
impossible via the mover, and any D-1 episode with one own unit must be a goal-selector cycle.**

**Theorem 3 (the detour is a forced move).** `occupied_now` contains the resolving unit's own
cell, so "stay where I am" is *not in the detour candidate set*. When the direct step is blocked
the unit **must** step somewhere, and the only ranking is distance-to-goal with a lexicographic
tie-break. It has no memory of the cell it came from (the function is a pure function of
`(view, commands)` — the bot's only persistent state is `announced`, `type_to_cut`,
`desired_second`, the opening flags and `regeneration_commitments`, 335).

### 1.2 The 194-turn no-op, reproduced turn by turn (MEASURED)

`m110` seat 1, class `choke_corridor`, opponent profile `harvester`. Geometry as materialised by
`fuzz_panel.materialize`:

```
 y=0  #############
 y=1  #1.##########
 y=2  #...........0        walkable row: x = 1..11 ; own tent '0' at (12,2)
 y=3  #############
 y=4  #############
own  unit 0 @ (11,2)  speed 1 cap 2 harvest 1 chop 1   carry -
own  unit 2 @ ( 4,2)  speed 2 cap 1 harvest 1 chop 0   carry -
opp  unit 5 @ ( 1,2)  speed 1 cap 2 harvest 1 chop 0
plants: BANANA (2,2) size 4 health 6 fruits 1 cooldown 48
own inventory [PLUM,LEMON,APPLE,BANANA,IRON,WOOD] = [0,0,0,2,0,0]
```

It is a one-cell-wide corridor. Resolver log (instrumented build, verified identical):

```
RES t=5  id=0 cur=(7,2) goal=(2,2) landing=(6,2) branch=DIRECT reserved={(4,2)}
RES t=6  id=0 cur=(6,2) goal=(2,2) landing=(5,2) branch=DIRECT reserved={(4,2)}
RES t=7  id=0 cur=(5,2) goal=(2,2) landing=(4,2) branch=DETOUR pick=(6,2)
                                   nbrs=[(5,3)#,(6,2),(5,1)#,(4,2)reserved]
RES t=8  id=0 cur=(6,2) goal=(2,2) landing=(5,2) branch=DIRECT reserved={(4,2)}
RES t=9  id=0 cur=(5,2) goal=(2,2) landing=(4,2) branch=DETOUR pick=(6,2)
...  identical pair repeated to t=200
```

Unit 2 emits `WAIT` on **every one of turns 1–200** and never leaves `(4,2)`. The goal of unit 0
is `(2,2)` on every single turn: the target selector is **not** at fault here. At `(5,2)` the
next step is the parked peer, the detour set is `{(6,2)}` because the corridor has width 1 and
the unit's own cell is excluded (Theorem 3), so it is *forced backwards*; from `(6,2)` the direct
step returns it to `(5,2)`. Final state at t200: BANANA still size 4 health 6 — never touched;
own score **2** (the two bananas it started with), opponent score **26**. Both own workers did
nothing for 194 turns.

**This is the whole 194-turn no-op.** It is not a tie-break subtlety; it is a one-cell-wide
corridor, an idle partner standing in it, and a mover whose action space excludes standing still.

### 1.3 Three distinct sub-mechanisms, not one (MEASURED)

Classifying all 35 episodes by the instrumented resolver log — *goal constant vs alternating*
and *detour branch taken vs not* (`classify.py`):

| shape | count | terminal (≥62) | signature |
|---|---|---|---|
| **M1 / M2 — goal constant, detour fires** ("D1-A") | 21 | 17 | one DIRECT leg + one DETOUR leg, or two DETOUR legs |
| **MIXED — detour fires *and* the goal also alternates** | 13 | 3 | both faults present |
| **M3 — goal alternates, detour never fires** ("D1-B") | **1** | 0 | `m085` s0, a *single* own unit |

Within the first group there are two geometrically different shapes, and they matter because
they need different fixes:

**M1 — corridor block.** The goal lies *beyond* the parked peer. One leg DETOUR (forced away),
one leg DIRECT (straight back). Example: `m110` above.

**M2 — same-target orbit.** The goal **is** the cell the parked peer stands on, and the two
oscillation cells are two neighbours of the goal, so **both** legs are DETOUR. Example `m014`
seat 1, unit 2 (193 turns):

```
own 0 @ (10,0) standing on the BANANA, emitting WAIT for turns 5..200
own 2 goal (10,0) every turn
RES t=7  id=2 cur=(10,1) goal=(10,0) landing=(10,0) DETOUR pick=(9,1)
RES t=8  id=2 cur=( 9,1) goal=(10,0) landing=(10,0) DETOUR pick=(10,1)
...  d((10,1))=1, d((9,1))=2 ; from (10,1) the free neighbours (10,2),(11,1),(9,1)
     all have d=2 and the lexicographic tie-break `*cell` picks (9,1).
```

Episodes with 100 % DETOUR (both legs) in the corpus: `m014` s1, `m094` s1, `m046` s0,
`m079` s0/s1 — all terminal.

**M3 — goal two-cycle in the scorer.** `m085` seat 0, one own unit, `reserved = {}`, both legs
`DIRECT`, and the *goal* flips every turn. Selector log:

```
at (1,4)  MOVE 0 9 1     57.143  Tree((9,1))     <- chosen
          PICK 0 LEMON   50.000  Cell((1,4))
at (2,4)  MOVE 0 0 5     62.500  Cell((0,5))     <- chosen
          MOVE 0 9 1     58.824  Tree((9,1))
          MOVE 0 1 4     46.875  Cell((1,4))
```

The cause is localised — it was previously recorded as "not localised in source". In
`endgame_candidates` (1233, reached permanently once `regeneration_commitments` is set, 1396–98)
the fruit-conversion candidate has **two mutually exclusive branches**:

- 1290–1302: if the unit is *adjacent to the tent*, price **only its own cell**:
  `score = 750/(conversion_turns + 3)`;
- 1303–1334: otherwise price **every** door cell: `score = 750/(travel + conversion_turns + 3)`.

At `(1,4)` (a door) the unit sees only `(1,4)`, whose conversion takes 12 turns → 750/15 = 50.
One step off the door it also sees door `(0,5)`, whose conversion takes 6 → 750/(3+6+3) = 62.5.
**The same plan is worth 25 % more one step away from the door than standing on it.** With the
competing tree candidate scoring between the two (57.1 / 58.8), the unit is in a strict
two-cycle. This is a Bellman-inconsistency: the value of a plan is not consistent between a state
and its own successor.

### 1.4 The question `local_claude_1` asked: how does the pair survive `compatible`?

Two answers, both MEASURED, and they mean different things.

**(a) In M1 the peer is not on the target cell at all.** `local_claude_1`'s correction is right
that "same-tree contention" is the wrong label for these. In `m110` the goal is `(2,2)`, the
peer is at `(4,2)`, and the peer's own command is `WAIT`. This is **path blocking**, exactly as
yamo's postmortem line 148 describes.

**(b) In M2 the peer *is* on the target cell, and `compatible` never sees it.** `compatible`
(643–654) opens with

```rust
if a==Target::None || b==Target::None { return true; }
```

`Self::wait()` (638–641) carries `target: Target::None`. So **a unit that has nothing to do is
invisible to the mutual-exclusion rule while remaining a physical obstacle.** In `m014` unit 0
stands on the banana emitting `WAIT` for 195 turns; unit 2 selects `Tree((10,0))` — the very cell
unit 0 occupies — and the pair passes `compatible` because unit 0's target is `None`. So the
exclusion rule was designed to stop two *workers* colliding, and does nothing about a worker
colliding with an *idler*. That is the single most important defect this analysis found, and it
is one expression wide.

I therefore correct my own earlier account
(`claude_1/banana-restoration-r2/feasibility-raw-zero-2026-08-07.md`) on two points: "same-tree
contention" describes only the M2 subset, not 34/35; and "34/34 have a parked adjacent peer,
30/34 with that peer standing on a plant" is true as a count but misleading as an explanation —
see 1.5.

### 1.5 Why the terminal mode never ends: the blocker is idle, not busy (MEASURED)

For every episode I measured, over the episode window, what the *other* own unit did
(`analyze.py`, `episodes.json`):

- **20 of 20 terminal episodes: the blocking peer emits `WAIT` on ≥ 95 % of the window and
  changes cell on 0.00 % of turns.** It never moves, at all, ever.
- Of the 15 short episodes, 13 have a peer that moves or works; those episodes end **when the
  peer finishes and moves**. `m040` s1 (the new two-worker case) is the clean example: unit 0,
  carrying 2 wood and heading to the tent at (9,0), bounces (4,0)↔(3,0) for exactly the 6 turns
  that the TRAIN-spawned unit 6 needs to finish `CHOP` at (5,0); at t86 unit 6 moves and unit 0
  walks straight through.

So the terminal/short split is **not** opponent aggression per se and **not** map class — it is
whether the blocker will ever move again. A working blocker bounds the episode by its own
remaining work. A permanently idle blocker makes it unbounded.

**Is D-1 measuring harm, or a unit pacing harmlessly while its partner works?** Measured: of the
19 games containing a terminal D-1 episode, **19 also violate P4** (no own progress in a rolling
60-turn window inside the live horizon). The partner is not working. It is harm.
(For completeness: 29 games violate P4 in total, and **10 of those have no D-1 at all** — so
"fix D-1" is not the same as "fix liveness", and D-1 should not be treated as the liveness
instrument.)

### 1.6 The condition behind the condition (MEASURED, with a correction of my own first number)

Because the terminal mode is really "a worker stopped working and stood in a doorway", I
measured idleness corpus-wide over all 240 games, per own unit, longest run of consecutive turns
emitting no command:

- naive: 207/240 games (86.2 %) contain an own unit idle ≥ 60 consecutive turns, median longest
  run 164 of 200 turns. **This number is mostly an artefact** — the panel simulates 200 turns of
  a 300-turn game on small maps, so worlds exhaust and idleness is legitimate.
- restricted to units that can actually work (`harvest_power > 0 or chop_power > 0`) **and** to
  the live prefix `fuzz_panel.live_horizon(tr)`, the honest figure is: median longest idle run
  **3** turns, but **37 of 364 capable own units (10.2 %) idle for ≥ 60 consecutive turns while
  the world still offers work**, and **19 (5.2 %) for ≥ 150 turns**.

Nineteen units idling ≥ 150 live turns against twenty terminal oscillation episodes is not a
coincidence: **the terminal oscillation population and the permanently-idle-worker population
are the same population, seen from opposite ends.** No detector currently names the idle unit;
D-1 only catches these games because the *other* unit paces against it.

### 1.7 One thing the task record suggests that I believe does not work

The record's §5 proposes porting the Gold-era **anti-stall watchdog**
(`rust/src/botmain/motion.rs:111–160`). I read it: it increments a stuck-streak only when
`entry.0 == cur.0 && entry.1 == cur.1` — *the troll did not move* — and sidesteps at streak ≥ 2.
**In every episode measured here the unit moves every single turn**, so `stuck` is false and the
streak resets to 0 forever. **The Gold-era watchdog would never fire on any of our 35 episodes.**
It is a stall detector, not an oscillation detector, and porting it is a non-fix. What *is*
portable from that file is `solve_moves` (162–260), whose two relevant properties are
`cs.push((t.pos(), 0)); // staying is always an option` (215) and
`.filter(|(_, pr)| *pr >= 0) // never retreat` (213) — see A4/B1 below.

### 1.8 INFERRED / UNRESOLVED

- **INFERRED**: the terminal mode is opponent-independent in cause; the reported association
  with non-aggressive opponents (`d1-mode-structure-2026-08-08.md`) is, on my evidence, a proxy
  for "the blocker had no work" rather than a board-churn effect. I did not test this directly.
- **UNRESOLVED**: whether the detour branch is yamo's own code or ours. yamo's postmortem says
  he "only set the destination"; this source *does* have a conflict resolver, so either the
  postmortem understates or the resolver is a local addition. Settling evidence: the original
  CodinGame submission source for agent 6593838, or yamo's published repository.
- **UNRESOLVED**: opponent units are not in `reserved` or `occupied_now` at all (736–737 filter
  `player == 0`), and are not obstacles in `bfs_distances`. Whether that produces its own stall
  class is untested. Settling evidence: an instrumented run counting turns in which an own MOVE
  lands on an opponent-occupied cell and the engine refuses it.
- **UNRESOLVED**: `m085`'s conversion-turn asymmetry (12 at `(1,4)` vs 6 at `(0,5)`) — I did not
  trace `conversion_chop_turns` far enough to say *why* the two doors differ. It does not change
  the diagnosis: the defect is that the on-door branch is exclusive.

---

## 2. What a fix must satisfy

Restating from the record, plus one clause I am adding on the evidence of §1.5:

1. **All 20 terminal episodes gone**, not fewer.
2. No de-novo oscillation and no fragmentation of long runs into short ones (the D176a failure).
3. **New, and I think decisive: the fix must restore *progress*, not merely remove *motion*.**
   §3 shows numerically that the obvious mover fix converts all 20 oscillations into 20 stalls,
   which zeroes D-1 and leaves the program exactly as uncontrolled as before. That is the
   owner's withdrawn category, arrived at from a different direction, and it must be tested
   against.

---

## 3. A numerical test of the obvious fix, run offline against the shipped bot's own decisions

Define two candidate mover invariants:

- **M (monotone-or-hold):** a landing with `d_goal(landing) > d_goal(current)` is illegal, and
  the unit's own cell is always a legal landing.
- **N (no immediate backtrack):** if `d_goal(landing) == d_goal(current)` then `landing` must
  not be the cell the unit occupied on the previous turn.

`invariant.py` recomputes, from the committed map geometry, the BFS distance to the *goal the
shipped bot actually held* for every resolver decision inside every episode, and classifies each
commanded step as ADVANCE / LATERAL / RETREAT. Result over all 35 episodes:

| | ADVANCE | LATERAL | RETREAT |
|---|---|---|---|
| 20 terminal episodes | 1 617 | **0** | **1 614** |
| 15 short episodes | 96 | **0** | 71 |

- **Every terminal episode is exactly `ADVANCE, RETREAT, ADVANCE, RETREAT, …`.** There is not a
  single lateral step anywhere in the corpus.
- Therefore **invariant M alone makes 34 of 35 episodes structurally impossible** — every
  RETREAT leg becomes a hold — including **all 20 terminal ones**. It does not touch `m085`
  (M3), where both legs advance toward *different* goals.
- **Invariant N is not needed for this corpus** but is needed for the argument to be a proof
  rather than an observation: without it a lateral A↔B cycle remains admissible.

And now the decisive consequence. Under M, in each of the 20 terminal episodes the unit holds
station — and the blocker **never moves** (§1.5, measured at 0.00 % on 20/20). So:

> **M alone converts 20 terminal oscillations into 20 terminal stalls.** D-1 would report 1
> episode instead of 35. P4 would still fail on the same 19 games. The 194-turn no-op would
> still be a 194-turn no-op — it would just stop moving while it did nothing.

This is why the mover fix cannot be the whole answer, and it is the strongest reason I have to
distrust any proposal judged by the D-1 count alone.

---

## 4. Wide list of possible actions

24 actions. Columns: **T20** = expected effect on the 20 terminal episodes; **cover** = which
sub-mechanisms it addresses (M1 corridor block / M2 same-target orbit / M3 goal two-cycle /
2W two-worker TRAIN case); **owner** = needs an owner decision.

### A. Architectural — explicit state and commitment

| # | action | T20 | cover | cost | risk | falsifier | owner |
|---|---|---|---|---|---|---|---|
| **A1** ✅ | **Per-unit one-turn position memory** in `YamoBot` (`BTreeMap<i32, Cell>` of last cell), used to enforce invariant **N** | 0 alone; completes the proof for B1 | M1 M2 2W | ~10 lines, one new field | first persistent per-unit state in the mover; must be reset on unit death/spawn | a corpus run showing a lateral 2-cycle survives | no |
| **A2** ✅ | **Goal commitment with invalidation**: a unit keeps last turn's target unless it is reached, becomes invalid, or a rival beats it by ε | 0 (they hold a constant goal already) | **M3** | ~25 lines | ε too small ⇒ no effect (M3's gap is 9.4 %); ε too large ⇒ stale targets, real value loss | `m085` still alternates at the chosen ε | yes — behavioural |
| A3 ❌ | Full **path commitment** (compute a path, store it, replan only on invalidation) | 20 | M1 M2 2W | large | biggest behavioural delta on a lineage we hold byte-sacred; unnecessary — the defect is one step deep | — | yes |
| **A4** ✅ | **Port `solve_moves`** from `rust/src/botmain/motion.rs:162–260`: joint landing assignment, staying always legal, never retreat, shuffle-invariant | 20 → stalls (§3) | M1 M2 2W | medium; needs the engine's swap/chain rules re-verified | replaces the resolver wholesale; *still leaves the stall* | a corpus run where P4 does not improve — predicted, see §3 | yes |
| A5 ➖ | Debug-build **design-by-contract assertions** on the mover (M and N checked at runtime, `debug_assert!`) | 0 | all | small | none shipped | — | no |

### B. Local — tie-break, hysteresis, symmetry

| # | action | T20 | cover | cost | risk | falsifier | owner |
|---|---|---|---|---|---|---|---|
| **B1** ✅ | **Monotone-or-hold detour**: drop `occupied_now.contains(cell)` exclusion of *the unit's own cell*, and filter the detour set to `d_goal(cell) ≤ d_goal(current)`. Two lines at 762–768 | **20** (measured, §3) | M1 M2 2W | ~4 lines | converts oscillation → stall; must ship with C5/C6 | any episode with a LATERAL leg (0 measured) | no |
| B2 ❌ | Randomised / salted tie-break (**D171a**) | ≤ 9 of 20 | M1 M2 | small | measured: 45.7 % cure vs an 80 % floor, +117 % displacement, 72 clean tasks acquired oscillation; also destroys the determinism the panel depends on | — | already closed |
| B3 ❌ | Preference tie-break with bounded arming (**D176a**) | 0 of 20 | M1 | medium | measured: fragmented long runs (5–9-turn bucket 213→825), worst run unchanged at 247 | — | already closed |
| B4 ➖ | Replace the lexicographic `*cell` tie-break with "prefer the cell I did not come from" | ≈20 | M1 M2 | small | a weaker form of A1+B1; no invariant, only a heuristic | — | no |

### C. Target selection and contention

| # | action | T20 | cover | cost | risk | falsifier | owner |
|---|---|---|---|---|---|---|---|
| **C1** ✅ | **Close the `Target::None` hole**: `Self::wait()` returns `Target::Cell(unit.cell)` instead of `Target::None`, so an idle unit owns the cell it stands on and no peer may target it (643–646, 638–641) | the M2 subset (≥ 5 of 20) | **M2** | one expression | changes candidate selection everywhere `WAIT` appears; a unit may be pushed to a worse plan; needs a full corpus run | a corpus run where M2 episodes persist, or where new episodes appear | no |
| **C5** ✅ | **Idle-yield rule**: an own unit whose selected command is `WAIT` and which lies on the shortest path between a working partner and that partner's goal must move to the nearest cell off that path | **20**, and converts them to *progress* not stall | M1 M2 2W | ~30 lines | a genuinely new behaviour; could displace an idle unit into a worse place; in a width-1 corridor the yield cell may be *past* the goal (in `m110`: `(1,2)`, reachable in 2 turns at speed 2) | a fixture where yielding does not restore progress | yes — new behaviour |
| C6 ✅ | **Idle parking discipline** (Gold-era "distinct camp-cell claiming", `motion.rs:22–107`): an idle unit walks to a claimed, distinct park cell near the tent instead of standing where it stopped | most of 20, structurally | M1 M2 | medium | may pull idle units away from where they will next be needed; costs movement | idle units still found on corridors in a corpus run | yes |
| C2 ➖ | **Elost owner rule** (a capable worker on a live tree owns it; do not send a second worker there) | the M2 subset only | M2 | medium | **measured limitation:** in `m014` the owner is *not capable* (chop 0 / no fruit) — it does nothing but would still own the tree. That is the right outcome here, but the rule as stated keys on capability | an M2 episode where the blocker fails the "capable" predicate | yes |
| C3 ➖ | Persistent exclusive target claims across turns (not just per-turn pair compatibility) | partial | M2 | medium | claims go stale; needs release rules | — | yes |
| C4 ❌ | Price contention into the scorer (penalise a candidate whose shortest path crosses a parked own unit) | unpredictable | M1 | small | a soft penalty buys no invariant; exactly the class of change that produced D176a's fragmentation | — | no |

### D. Detection-side — a self-check the bot performs

| # | action | T20 | cover | cost | risk | falsifier | owner |
|---|---|---|---|---|---|---|---|
| D1 ➖ | **Bot-side oscillation net**: keep the last 3 cells per unit; if `p[t] == p[t-2] ≠ p[t-1]` with no progress event, blacklist the repeated cell for k turns and re-select | 20, as a net | all incl. unknown | ~25 lines + state | treats the symptom; can *hide* a future root cause | — | no, if paired with the counter below |
| D2 ✅ | **Observability**: when D1 fires, emit `MSG` and increment a counter the regression tests assert is **zero** on the fixture corpus | 0 | all | tiny | none | — | no |

D1 is the only action that covers mechanisms we have not yet discovered. I would ship it *only*
with D2, so that it can never silently absorb a new defect.

### E. Structural — make the ambiguity impossible

| # | action | T20 | cover | cost | risk | falsifier | owner |
|---|---|---|---|---|---|---|---|
| E1 ➖ | Goal-relative rather than absolute cell ordering in the detour tie-break | 0 | — | small | breaks the M2 symmetry but not the cycle | `m014` still orbits | no |
| E2 ➖ | Forbid selecting any target cell currently occupied by an own unit (a stronger C1) | the M2 subset | M2 | small | over-restrictive: forbids relieving a partner on a tree | value regression on the panel | yes |
| E3 ❌ | Treat own units as **non-walkable** in `bfs_distances`/`next_cell` | 0 of 20 | — | medium | in a width-1 corridor the goal becomes unreachable, `next_cell` returns `current`, and the unit stalls — the same non-fix as §3, with worse path quality elsewhere | — | no |
| E4 ➖ | Treat **opponent** units as obstacles too (currently `player == 0` only) | 0 known | unknown | small | unmeasured; may be a real latent defect (§1.8) | an instrumented count of refused MOVEs | no |

### F. Testing-side

| # | action | cover | cost | owner |
|---|---|---|---|---|
| **F1** ✅ | **R-6 frozen-fixture regression suite** — the named deliverable, specified in §6 | M1 M2 M3 2W | ~150 lines of test + 4 fixtures | no |
| **F2** ✅ | **R-7 mover contract test** — a table-driven property test asserting M and N directly on the resolver for enumerated geometries incl. the width-1 corridor | M1 M2 | ~80 lines | no |
| F3 ✅ | Add episode-**length distribution** to the panel report (diagnosis) **without** relaxing the gate condition | — | small | no |
| F4 ✅ | **Anti-overfit control**: the `m040` fixture asserts the bot still gets through a *working* blocker and does not simply freeze near partners | 2W | small | no |
| F5 ➖ | Byte-stability assertion on the fixtures' command streams so unrelated changes are visible | — | small | no |

### G. Change what we require

| # | action | verdict |
|---|---|---|
| G1 ❌ | Relax the gate to "no terminal oscillation" | **Rejected, and I reject it on my own evidence as well as the withdrawal.** §1.5 shows the short episodes are bounded by a *working* blocker — a genuinely different and benign situation — so the relaxed threshold is superficially defensible. But it would make the 194-turn no-op invisible to the gate the moment a fix shortened it to 61 turns, and 19/19 terminal games also fail P4, so the gate would be relying on a second instrument to catch the thing the first one stopped naming. It hides what we do not control. |
| G2 ❌ | Repair only the gate's reference build, not the shipped bot | **Rejected.** Withdrawn by the owner and correctly so: it certifies an instrument while the shipped program keeps the defect. |
| G3 ❌ | Redefine D-1's predicate as "no *player-level* progress" instead of "no *unit-level* progress" | **Rejected — this is G1 in disguise.** It is tempting: I measured 19/19 terminal games also failing P4, so it would retain every terminal case while dropping the 15 short ones. But the mechanism is the same in short and long episodes; the only difference is how long the blocker stays parked. Narrowing the predicate would delete the early warning and keep only the disaster. |
| G4 ❌ | Change the opponent mix / map generator so the precondition is rarer | **Rejected.** It changes the measurement, not the program, and would erase the `choke_corridor` class that finds this. |
| G5 ❌ | Do nothing, with an argument | **Rejected under the stated objective.** The +0.045 value closure remains valid and untouched — nobody should argue this raises score. But the objective is control, debt and coverage, and §1.6 shows the defect is the visible tip of a condition affecting 10.2 % of capable workers. |

Legend: ✅ recommended · ➖ optional / conditional · ❌ not recommended.

**Counts: 24 actions generated; 11 recommended (A1, A2, A4, B1, C1, C5, C6, D2, F1, F2, F3/F4),
6 optional, 7 explicitly rejected.**

---

## 5. Recommendation

**Do not ship a mover fix alone. Ship a paired change, and let the test suite be the deliverable
rather than the diff.** In priority order:

**R-1 (the test comes first, and it can land now).** F1 + F2 — the R-6 fixture suite and the R-7
mover contract test, committed **red**. This is the only item that is fully within the current
boundary once analysis is approved, it delivers the owner's named artefact directly, and it
converts "we think we understand this" into "the repository asserts it". It also protects every
later step from the D176a failure mode of judging a fix by counts.

**R-2 (the mover invariant).** B1 + A1: monotone-or-hold plus one turn of position memory.
Measured to make 34/35 episodes structurally impossible (§3), four lines plus one field, no tie-
break heuristics, and it states a property rather than tuning a preference. **It must not be
shipped on its own** — on my own numbers it would convert 20 oscillations into 20 stalls and
zero the D-1 count while changing nothing about control. Its regression proof is clause (a) of
R-6; its *insufficiency* proof is clause (b).

**R-3 (the actual cure for the terminal mode).** C5 (idle-yield), with C1 (close the
`Target::None` hole) as the cheap partial that lands first. This is what turns the stall into
progress: 20/20 terminal blockers are permanently idle and never move, so nothing short of
making the idler move can restore the game. C6 (idle parking discipline) is the structural form
of the same idea and is the better long-term shape.

**R-4 (D1-B).** A2 (goal commitment) as the general invariant, and the localised repair of the
exclusive on-door branch at 1290–1302 as the root-cause fix — a unit standing on a door should
price the other doors too, which removes the value discontinuity that creates the two-cycle.
1 episode of 35, 0 of 20 terminal; low urgency, but it is now *localised*, which was the
outstanding blocker for a raw-zero rule (a conjunctive rule needs D1-B closed too).

**Justification against the owner's four words.**
*Control*: R-2 replaces "the minimiser happens not to send it back" with a stated invariant.
*Technical debt*: R-3 removes a rule (`Target::None` compatibility) that was silently doing
nothing for the case it looks like it covers, and gives idle units a defined behaviour instead
of an accidental one. *Test coverage*: R-1 covers three mechanisms plus the two-worker case with
frozen fixtures that cannot drift with the map generator. *Understanding*: this document
names three mechanisms where the record had one, localises D1-B, kills the watchdog port, and
supplies the number that says the obvious fix is not a fix.

**Coverage:** D1-A (M1, M2) — covered by R-2 + R-3. D1-B (M3) — covered by R-4, and localised
here for the first time. The two-worker TRAIN case (`m040`) — covered: it is an M1 with a
*working* blocker, R-2 makes the bounce a one-turn hold and it resolves at t86 exactly as it
does today; F4 is the control that proves the fix did not simply freeze the unit.

---

## 6. The named deliverable: what test fails if the 194-turn no-op can ever happen again

**R-6 "blocked-corridor liveness"**, added to
`claude_1/banana-restoration-r2/regression_tests.py` alongside `r5_two_worker_full_cargo_banking`,
with four **frozen literal fixtures** added to `make_banana_traces.py` as
`scenario_r6a_corridor_block()` … `scenario_r6d_working_blocker()`.

They must be **literals, not calls into `fuzz_panel.build_skeleton(110, …)`** — the generator is
seeded and would silently produce a different map the day the class mix, seed list or
regeneration-attempt counter changes.

### Fixture R-6a — the 194-turn no-op itself (verbatim from `m110` seat 1)

```
rows      = ["#############",
             "#1.##########",
             "#...........0",
             "#############",
             "#############"]
units     = [[0, 0, 11, 2, 1, 2, 1, 1,  0,0,0,0,0,0],   # own, chop-capable
             [2, 0,  4, 2, 2, 1, 1, 0,  0,0,0,0,0,0],   # own, chop 0 -> idles
             [5, 1,  1, 2, 1, 2, 1, 0,  0,0,0,0,0,0]]   # opponent
plants    = [["BANANA", 2, 2, 4, 6, 1, 48]]
inventory = [0, 0, 0, 2, 0, 0]
opponent  = fuzz_panel 'harvester' profile ; turns = 200
```

Run the shipped binary closed-loop through `regression_tests.run_binary_custom`, build the trace
with `trace_detectors.build_trace`, then assert **all three** clauses. Each is independently
sufficient to fail, and each blocks a different way of faking a fix:

- **(a) no alternation.** `td.detect_d1(tr)["count"] == 0`.
  *Blocks the defect itself.* Currently **FAILS**: one episode, `unit 0, turns 6–200,
  cells (6,2)/(5,2)`.
- **(b) liveness.** For every rolling 60-turn window ending before `fuzz_panel.live_horizon(tr)`,
  the own inventory score or some own unit's cargo changes.
  *Blocks "fix" = turn the oscillation into a stall* — precisely the outcome §3 predicts for a
  mover-only change. Currently **FAILS** (this game is a P4 violation).
- **(c) the job gets done.** By turn 200 the own inventory differs from its initial value **and**
  the plant at `(2,2)` has had `health` or `size` reduced at least once.
  *Blocks "fix" = abandon the goal so the bounce stops.* Currently **FAILS**: final inventory is
  the starting `[0,0,0,2,0,0]`, score 2, and the banana is untouched at size 4 health 6.

That is the answer to the owner's question. **If the 194-turn no-op could ever happen again,
R-6a clause (a) fails on the exact geometry, and clauses (b) and (c) fail with it.** If a future
change makes the unit stand still instead of pacing, (a) passes and **(b) still fails**. If a
future change makes it give up on the tree, (a) and (b) may pass and **(c) still fails**.

### Fixture R-6b — the same-target orbit (`m014` seat 1)

Blocker standing **on the goal cell**, both legs DETOUR — the shape that exercises the
`Target::None` hole and that R-6a does not reach. Same three clauses. Currently FAILS (a):
`unit 2, turns 7–200, cells (10,1)/(9,1)`.

### Fixture R-6c — the goal two-cycle (`m085` seat 0)

**One own unit only**, so by Theorem 2 the mover cannot be involved; this is the D1-B guard.
Clause (a) only, plus an added clause: the unit's selected `Target` must not alternate with
period 2 over any window of ≥ 6 turns without an intervening progress event. Currently FAILS:
`unit 0, turns 17–23, cells (1,4)/(2,4)`, goals alternating `Tree((9,1))` / `Cell((0,5))`.

### Fixture R-6d — the working blocker, anti-overfit control (`m040` seat 1)

The TRAIN-spawned two-worker case. Assertion is deliberately **weaker**: any D-1 episode must be
≤ the blocker's remaining chop turns at the episode start, **and** clause (c) must hold. This
fixture must **pass after the fix as it effectively does today** (the bounce lasts 6 turns and
resolves). Its job is to fail if a fix works by making units freeze whenever a partner is near.

### Non-vacuity controls

In the existing `control_*` style (`control_r5_oscillator` is the model): one scripted mutant per
shape that reproduces the pattern and **must** fail the corresponding clause, so a future
refactor cannot make R-6 pass by accident.

### R-7 — the mover contract test (the coverage/understanding deliverable)

A table-driven test over the resolver, run on enumerated geometries — width-1 corridor, T
junction, open field, blocker-on-goal, two movers crossing — asserting for every own unit:

- **M**: `d_goal(landing) ≤ d_goal(current)`;
- **N**: if `d_goal(landing) == d_goal(current)` then `landing ≠ previous cell`;
- **liveness of the action space**: the unit's own cell is always among the admissible landings.

R-7 is the test that writes down what we believe the mover guarantees. It is cheap, needs no
game, and it is the artefact that makes the next person's change safe. Today M and N are simply
**not** properties of the shipped resolver — measured 1 685 RETREAT steps inside D-1 episodes
alone — so R-7 lands red and stays red until R-2 ships.

---

## 7. Summary of what this answer changes about the shared account

1. There are **three** mechanisms, not one: corridor block (M1), same-target orbit (M2), goal
   two-cycle (M3). The record's single "memoryless detour tie-break" account covers M1 and M2
   and is silent on M3.
2. `local_claude_1` is right that "same-tree contention" is the wrong global label — but the
   same-target case is real, and it survives `compatible` because **`Target::None` is
   unconditionally compatible** (line 644). That is the specific hole.
3. **D1-B is now localised**: `endgame_candidates` 1290–1302, the exclusive on-door pricing
   branch. It was previously recorded as not localised in source; that blocked a conjunctive
   raw-zero rule.
4. The terminal/short split is explained by **whether the blocker is permanently idle** (20/20
   terminal, 0.00 % movement) rather than by opponent aggression.
5. **The Gold-era anti-stall watchdog would never fire on any of our 35 episodes.**
6. **The obvious mover fix, measured offline against the shipped bot's own decisions, removes
   34/35 episodes and restores progress in none of them.** Any proposal — including my own —
   must be judged on liveness, not on the D-1 count.
7. My own earlier "30/34 with the peer standing on a plant" was a true count and a misleading
   explanation; the peer standing on a plant is usually *not working it*.
