# G-1 execution — the dance geometry measured (M-1 and M-2), 2026-08-25

Task `20260825-dance-geometry-measurements`. Definitions of record:
`claude_1/geometry1/definitions-g0-2026-08-25-r2.md`, **DEFINITIONS_ACCEPTED** by codex_1
(`20260825T142509Z`). Code: `claude_1/geometry1/geometry.py`, `claude_1/geometry1/run_geometry.py`.
Results whole: `results/geometry-2026-08-25.json` (every episode, every eligible turn),
`results/controls-2026-08-25.json`, `results/determinism-2026-08-25.json`.

**Carried on every number below: D-1 off replays is an UPPER BOUND** — the adapter reconstructs
plant clocks and the reconstruction error direction *invents* dances. The two reads are different
days and opponent fields with no randomisation, and the counts are small. Nothing here decides a
bug, a cure, or a candidate; it measures two things that were unmeasured.

---

## For the owner, in plain words

Two questions had never been answered with numbers.

**M-1 — when one of our own trolls stands next to a dancing troll, is there a way around it, and
what does the detour cost?** The answer is that usually there is **no way around at all**. On the
older read, on **91.20 %** of the turns we could measure, the teammate was standing on **every**
shortest road to the dancer's own stated goal. On **439** of those turns — nearly a third of the
whole population — removing that one teammate's square left the goal **unreachable**: the maps are
small (one game's walkable area is 76 squares) and the teammate is standing in a doorway. Of the older read's
80 dances, **23** have a typical detour cost of *infinite* — no road around at all — and **26** have
a typical cost of one or two squares; pooled with the newer read's 25 dances that is **29** infinite
and **40** at one or two squares out of 105.

**M-2 — on the older dances that had "nobody next to the dance when it began", what was actually
standing on the square the dancer wanted to step to?** In **60 of the 68** backward steps, one of
our own trolls was on that square: **27** had been standing there for at least two turns, **33**
had just arrived or were about to leave, and only **8** had nothing of ours on it. So "nobody
adjacent when it started" does **not** mean "nothing in the way" — the teammate arrives during the
dance.

**Both facts point the same way for the open question** (swap the standing teammate once, or route
around it): **routing around is usually not available.** I make no recommendation; that is the
coordinator's and the owner's call.

---

## M-1 — the road around the standing teammate

Population: 105 episodes, **0 refusals** — the older read's 80 (batches 1–3, 469 games) and the v4
read's 25 (160 games). Cost-bearing eligible turns: **1,432** older, **420** v4.

| read | blocked (`d1 > d0`) | of cost-bearing eligible | of which unreachable (`∞`) | lateral step existed (UPPER BOUND) |
|---|---|---|---|---|
| older | **1,306** | 1,432 (**91.20 %**) | **439** | 677 of 1,306 (**51.84 %**) |
| v4 | **328** | 420 (**78.10 %**) | **55** | 126 of 328 (**38.41 %**) |

Non-cost-bearing statuses are counted, never dropped: `TARGET_OCCUPIED` 10 older / 15 v4 (the
teammate is standing **on** the target, so `d1` is meaningless and the turn is excluded);
`TEAMMATE_ABSENT`, `TEAMMATE_ON_DANCER_CELL`, `OFF_BASELINE_MAP` **0** on both reads. Ineligible
window turns: `ineligible_no_target` 6 older / 2 v4, `ineligible_no_successor` 3 / 4,
`ineligible_dancer_absent` 0 / 0. K-5 reconciles all 105 episodes exactly.

**`blocked_but_road_exists` = 0 on both reads.** Not one turn had a zero-cost road around while the
arm still could not step forward. The evidence for "route around instead of swapping" is therefore
**empty**, and the evidence the other way — 439 + 55 unreachable turns and 29 of 105 episodes at
median cost `∞` — is what the read carries.

### cost class × shape (episodes)

| read | class | one-cell | adjacent | nobody |
|---|---|---|---|---|
| older | `0` | 0 | 1 | 5 |
| older | `1–2` | 14 | 6 | 6 |
| older | `3–5` | 6 | 5 | 1 |
| older | `>5` | 4 | 4 | 5 |
| older | `inf` | 10 | 5 | 8 |
| v4 | `0` | 1 | 0 | 1 |
| v4 | `1–2` | 9 | 5 | 0 |
| v4 | `3–5` | 2 | 1 | 0 |
| v4 | `inf` | 3 | 3 | 0 |

Shapes are the coordinator's own (`reread_shapes.describe`, K-7): older 34 one-cell / 21 adjacent /
25 nobody; v4 15 / 9 / 1. No episode is class `n/a` — every window had at least one eligible turn.

### cost class × dance length (episodes)

| read | class | 7–11 turns | 12–29 | ≥30 |
|---|---|---|---|---|
| older | `0` | 5 | 0 | 1 |
| older | `1–2` | 11 | 9 | 6 |
| older | `3–5` | 8 | 2 | 2 |
| older | `>5` | 10 | 2 | 1 |
| older | `inf` | 17 | 0 | 6 |
| v4 | `0` | 1 | 1 | 0 |
| v4 | `1–2` | 3 | 7 | 4 |
| v4 | `3–5` | 3 | 0 | 0 |
| v4 | `inf` | 5 | 1 | 0 |

The `inf` class concentrates in the **short** dances (17 of 23 older `inf` episodes are 7–11 turns).
A short dance is where the road around does not exist.

---

## M-2 — what stood on the dancer's forward cell on each backward step

Backward steps are the imported instrument's own `MOVED_REGRESSIVE` verdicts
(`regressive_baseline.measure_game` through its `row_sink`), restricted to the dancer inside the
window. The partition is r2 §R3: identity-aware, mutually exclusive, `UNDETERMINED` where a
neighbouring turn is missing.

| read / shape | episodes | (a) standing | (b) transient | (c) nothing of ours | UNDETERMINED |
|---|---|---|---|---|---|
| older, all | 80 | **561** | **64** | **9** | **0** |
| older, one-cell | 34 | 387 | 14 | 0 | 0 |
| older, adjacent | 21 | 147 | 17 | 1 | 0 |
| **older, nobody (the charter's headline)** | **25** | **27** | **33** | **8** | **0** |
| v4, all | 25 | 188 | 10 | 0 | 0 |

**`UNDETERMINED` is 0** — every boundary turn the partition needed was present in the trace, so no
row was defaulted and none had to be. The nine residual (c) rows are listed whole in the results
JSON and reproduced here, as the charter requires:

| game / seat | shape | turn | dancer | forward cell | target | forward cell off the BFS map | target changed this turn |
|---|---|---|---|---|---|---|---|
| 900091110/0 | nobody | 135 | (11,4) | (11,5) | (12,5) | no | no |
| 900092186/0 | nobody | 22 | (9,4) | (9,5) | (8,9) | no | no |
| 900092700/1 | adjacent | 2 | (11,2) | (11,3) | (12,10) | no | no |
| 900092998/0 | nobody | 111 | (10,4) | (10,3) | (10,2) | no | no |
| 900093265/0 | nobody | 80 | (11,6) | (11,5) | (10,4) | no | **yes** |
| 900100880/0 | nobody | 25 | (3,2) | (4,2) | (13,6) | no | **yes** |
| 900101148/0 | nobody | 118 | (14,7) | (13,7) | (7,3) | no | no |
| 900107799/0 | nobody | 133 | (11,4) | (10,4) | (3,3) | no | no |
| 900110085/0 | nobody | 71 | (7,1) | (8,1) | (8,0) | no | no |

None is a Manhattan-fallback row; two coincide with a planner flip of the stated target.

---

## Controls, each with its number

| control | number | verdict |
|---|---|---|
| **K-1** positive, `R` on the v4 read | 191 / 198 = **96.46 %** against the 95 % bar | **PASS** (see the finding below) |
| **K-2** negative, `P` on the v4 read | 217 of 228 forward cells free; **11 exceptions, all explained** | EXCEPTIONS — ALL EXPLAINED |
| **K-3** poison | 1,852 draws, seed `20260825`; blocked **21** = **1.13 %** against the measurement's 88.2 % | reported, not asserted |
| **K-4** determinism | two runs, separate directories, both files byte-identical | **PASS** |
| **K-5** exhaustiveness | 105 of 105 episodes reconcile; 0 off; 0 refused | **PASS** |
| **K-6** `arm_transient` on the v4 letters | `R/False` **197**, `R/True` **1**; `H` population **0** | `H` half **VACUOUS — NOT MEASURED** |
| **K-7** re-read identity | recomputed `8e2159e3…` == published `8e2159e3…` | **PASS** |
| **K-8** peer uniqueness | 105 episodes, 0 refused for multiple/no peer | **PASS** |
| **K-9** v2 shim fidelity | 865 turns checked, **0** mismatches | **PASS** |
| shape join one-to-one (added at execution) | 105 keys for 105 episodes; **1** collision under a position-derived key | **PASS** |

**K-3 is the control that carries the M-1 result.** Walling one random far cell instead of the
teammate's cell blocks the dancer on **1.13 %** of the same turns; walling the teammate's cell
blocks it on **88.2 %**. The measure is measuring the teammate, not the map's narrowness.

**K-2's eleven exceptions are explained by the arm's own code, not by a story.** The `P` branch
(`cure1-hold-v4.rs:872`) tests `reserved` and `landing_forbidden` — **not occupancy** — and
`reserved` is initialised (`:833`) to the cells of own units that are **not moving this pass**. All
eleven occupants are movers under the arm's own `moving_ids` projection, so their cells were never
reserved and `P` is correct. The expectation in the definitions ("a `P` turn has a free forward
cell") was the wrong expectation; the arm never promised it.

**K-6's single `R/True` is the empirical confirmation of §R4a's N-2.** The one `R` turn whose
`arm_transient` is true (game **900326532**, turn 12) is in a **scope-disabled** game — exactly
where `hold_enabled` is false (`:938`) and `R` can be emitted on a transient block. The other 197
`R` turns are `arm_transient == False`, as the counter argument predicts for scope-active windows.
The `H` half is **VACUOUS — NOT MEASURED**, never "passed": there are no `H` turns inside these
windows.

---

## Findings — three, all found by execution, none of them cosmetic

**F-1 — the accepted K-1 category table has no row for a non-cost-bearing status, so seven fully
explained rows land in the "unobservable" bucket. §R4a's *stop and ask* therefore fires, and I am
firing it.** All seven K-1 disagreements are the **same** observable thing: game **900327649**,
turns 72–84, `status == TARGET_OCCUPIED` — the teammate is standing **on the target cell**, so
`d1 > d0` is not computed and the row cannot agree by construction. The proving field is
`row.status`, which the definitions already record on every row. Under §R4a these rows are
scope-active and non-first-turn, so a non-empty residual triggers *stop and ask*: **I am reporting
it rather than re-categorising under my own authority.** The residue is demonstrably a measurement
artefact and not unobservable resolver state, so K-1's 96.46 % stands; what needs a ruling is
whether §R4 gains a `NON_COST_BEARING_STATUS` category in an r3, and whether such turns should be
excluded from K-1's population entirely (which would make K-1 191/191 = 100 %). **I have not made
that change.** Both numbers are on the record.

**F-2 — a position-derived episode key silently merges two real episodes, and it moved a published
count by one.** The older read carries **two distinct episodes with the same
(game, seat, window start)** — `900093265` / seat 0 / turn 80. Joining the coordinator's shapes on
that derived key merged them and produced 24 nobody / 22 adjacent instead of the correct **25 / 21**.
The join now uses the episode's own index in its source list and **asserts one-to-one** before any
table is built; the assertion is published as `shape_join_one_to_one` with its collision count. This
is the same failure shape as O-1 (`f3_peers[0]` in roster order): a key that *happens* to be unique
is not a key. I propose it as a standing control **K-10** for codex_1 to rule on at G-1 review; the
published tables already use the corrected join, and the corrected shape counts match the
coordinator's own re-read note exactly (34 / 21 / 25).

**F-3 — the arm's `moving_ids` must be reconstructed from the chosen target, not from the replayed
verb.** The replay's command line is **post**-resolution: a denied mover appears as `WAIT`. The
arm's `moving_ids` (`:826–831`) is a **projection** — `next_cell` from the target the unit chose
that turn, mover iff the landing differs from the current cell. Using the verb instead makes
`arm_transient` and K-2's explanation wrong on exactly the denied movers the measurement is about.
The runner reconstructs the projection. This is a faithfulness fix inside the accepted definition of
`arm_transient` ("the arm's exact predicate"), not a change to it, and it is stated here rather than
left in the code.

---

## What this does not say

It does not decide Candidate 2 or 3, does not re-open the accepted r3 classification or its counts,
does not touch the parked Candidate 1 verdict, and asserts nothing about any opponent's reasons.
`lateral exists` remains an **upper bound** — the arm also excludes `reserved` and
`forbidden_for_non_priority`, which a replay does not carry. No Arena action, submission, fetch,
TestSession or sealed-map access occurred; the only writes are under `claude_1/geometry1/**`.

## Reproduction

```
python3 claude_1/geometry1/run_geometry.py \
    --inputs <dir with the pinned replays at their repository paths> \
    --reread <origin/main:local_claude_1/dance-geometry/reread_shapes.py> \
    --out <dir> [--peer <second run's dir>]
```

The runner refuses on any import-digest or input-digest mismatch. Pinned inputs verified this run:
`facts80` `7cd3631c…`, `g2-grade` `45f5f22a…`, v3 replays `01169944…c3ceb`, v4 replays
`050d1ceb…c6a38`, `reread_shapes.py` `7c2c4b95…`.
