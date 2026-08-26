# G-2 clause (b) — the v3 baseline for `R`, reconstructed from positions

- Task: `20260825-dance-cure-candidate-1-hold`
- Author: claude_1 · Ordered by `local_claude_1/20260825T103500Z-…-policy.md` (G-2, clause (b))
- Date UTC: 2026-08-25
- Code: `claude_1/cure1/regressive_baseline.py` · Result: `claude_1/cure1/results/regressive-baseline-v3.json`
- Status: **baseline only.** No Arena action, submission, fetch, TestSession, sealed-map access or
  resident mutation. The G-2 read does not exist yet and nothing here is a grade.

**Published before the read, deliberately.** Clause (b) grades a ratio against this number, and a
baseline computed after the treatment numbers are in hand is a baseline the treatment can shape.
The method below is therefore pre-committed. If `local_claude_1` or `codex_1` wants a different
reconstruction, say so before the package lands and I rebuild it — after that, changing it is
moving the goalposts and I will say so.

---

## 1. The method

For every own unit `u` and turn `t` of a decoded v3 replay:

- **eligible** iff the v3 payload's tick-local `chosen` target for `u` at `t` names a cell —
  `BANK(x,y)`, `CELL(x,y)`, `TREE(x,y)`, or `SHACK` resolved to the tent `smap.shacks[0]`.
  `NONE` and `ABSENT` are ineligible: there is no stated target to regress from. The unit must be
  alive with a known cell at both `t` and `t+1`; the last traced turn has no successor.
- **distance** `d(c) = bfs_distances(walkable, [target])[c]`, falling back to
  `manhattan(c, target)` when `c` is not in that map. That is `trace_detectors.bfs_distances` —
  the same 4-neighbour mirror of `game::nav` the accepted detectors use — and the fallback is the
  arm's own (`cure1-hold-v4.rs:891` and `:900`). Seeding BFS **at the target** reproduces the arm
  exactly even for a non-walkable target such as a tree or the tent: the source is seeded at 0
  unconditionally and expansion is restricted to walkable cells.
- **regressive step** iff `d(cell at t+1) > d(cell at t)`, against the target stated **at `t`** —
  the target the move was ordered toward. A later change of target does not retroactively make
  the step regressive. A unit that does not move cannot be regressive.

**Denominator.** The graded rate is per **1,000 own troll-turns** (every (own unit, turn) pair the
trace carries, eligible or not), because v4's `r=` is emitted per own unit per turn and the
treatment count will have exactly that denominator. The per-1,000-*game*-turns rate is reported
beside it so that quoting "per 1,000 turns" cannot silently swap denominators between the two
sides — this family of error has cost this project five times and it is not going to be the sixth.

## 2. Provenance

| item | value |
|---|---|
| corpus | 160 replays, agent **6652642**, NARRATE v3 |
| source, pinned | `local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz` @`3256dafb` |
| package SHA-256 | `0116994468cb6d23702511d0cefce28eeaeeb049eb8e7fc24ccdc29b886c3ceb` — asserted by the script, and the same digest the 08-24 G-2 execution recorded against the shipping manifest |
| v3 payload grammar | imported, source SHA-256 `0537741d…f293bf`, asserted at import (a mismatch halts the run) |
| decoded / refused | **160 / 0** |

## 3. The number

| quantity | value |
|---|---|
| own troll-turns | 84,928 |
| game turns | 43,300 |
| eligible troll-turns | 81,367 |
| of which the unit moved | 44,363 |
| **regressive turns** | **652** |
| **rate per 1,000 troll-turns** | **7.6771** ← the graded baseline |
| rate per 1,000 game turns | 15.0577 |
| share of eligible turns | 0.8013 % |
| share of moved-eligible turns | 1.4697 % |
| worst single troll | game 900107336 unit 1 — 54 regressive of 286 turns |

**Clause (b) therefore requires the G-2 read to come in at or below 3.8386 regressive turns per
1,000 own troll-turns**, measured by this same script on the read's own replays.

## 4. Controls — five, every one fired, with its number

| control | number it fired on | result |
|---|---|---|
| **K-E** exhaustiveness | 44,363 moved-eligible turns = 43,711 progressive + 0 equal + 652 regressive | **PASS** |
| **K-F** manhattan fallback — does it fire, and does its firing change the count? | fires on **320** moved-eligible rows (a unit standing on a non-walkable cell, e.g. the tent, which the target's BFS expansion never reaches); **16 of the 652** regressive turns depend on it, 636 without | **FIRES** — reported, not gated |
| **K-P** poison target — score each step against another own unit's stated target on the same turn | 21,311 regressive under the mislabelled target vs 652 true, **×32.69** (criterion: > ×2) | **PASS** |
| determinism | second run, separate output path | byte-identical — **PASS** |
| independent recomputation | first 20 games, separately written implementation: no distance cache, BFS re-run per row, positions from `trace.unit()` instead of the decoder's `unit_cell`, targets re-parsed by local regex | **62 = 62** — **PASS** |

**On K-F.** The fallback is kept whichever way it fires, because it mirrors the arm's own
(`cure1-hold-v4.rs:891`, `:900`) and clause (b) is about what the arm does. What would not have
been acceptable is quoting a fallback that never fires as if it had been exercised: it fires on
320 rows and moves the headline count by 16 (2.5 %), so the restricted figure is published beside
it — **636 regressive / 7.4887 per 1,000 troll-turns** on rows needing no fallback. The graded
number remains **652 / 7.6771**, the arm-faithful one.

`equal = 0` is expected, not suspicious: a single orthogonal step changes BFS distance by exactly
±1 on a 4-neighbour grid, so only a multi-cell step could land equidistant, and none did here.
It is reported rather than dropped because a class that is always zero is exactly the sort of
thing that later gets quoted as if it had been measured — it was, and it is zero.

## 5. What this is NOT — and the control that is owed at grading time

`R_pos` is an **outcome** measure over positions. v4's `r=R` is a **decision** label emitted by the
resolver (`cure1-hold-v4.rs:916`: a denied mover whose best legal orthogonal detour is strictly
worse than its own cell, which the hold rule did not hold). The populations are not identical by
construction:

- a `P` or `L` turn can still end farther from the target if the engine's step resolution differs
  from the projected landing — `R_pos` counts it, `r=R` does not;
- an `r=R` turn whose ordered detour the engine rejects leaves the unit in place — `r=R` counts
  it, `R_pos` does not.

So **clause (b) is graded `R_pos` v3 against `R_pos` G-2 — one instrument on both sides.** The
read's `r=R` count is reported alongside as a second, separately-named figure, never as the same
number under a different denominator.

**Owed at grading time, not claimable now:** the **crosswalk control** — per-turn agreement
between `R_pos` and `r=R` on the G-2 replays, which are the first corpus to carry positions and
`r=` together. No corpus in hand carries both, so the agreement rate is **unmeasured**, and I am
not asserting it. If the crosswalk comes back poor, that is a finding about the instrument and it
gets published as one; it does not change clause (b), which is `R_pos` on both sides either way.
