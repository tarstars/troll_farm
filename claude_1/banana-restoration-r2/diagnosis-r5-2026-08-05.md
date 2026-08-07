# Diagnosis R-5 — two-worker full-cargo banking oscillation (round 5, RED)

Date: 2026-08-05
Candidate: `candidate-banana-r2.min.rs`, SHA-256
`9f5ef8336c5268927dd3aef873a1a348dd9e0bb43c2cc1e505b14730352db8a2`
Parent: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
(`a8eb3b2b...`)
Ground truth: round-4 host review
(`origin/agent/local_codex_1:data/analysis/live-agent-6553250/banana-restoration-r2-round4-host-review-2026-08-05.md`),
terminal failure 1: on map seed 9,854,000 seat 0 vs `gold_adaptive`, worker 2
(carry `[0,0,0,0,0,2]`, free_capacity 0) alternates `(8,4)<->(8,3)` for 225
turns (t34-t258), emitting `MOVE 2 8 3` / `MOVE 2 8 4`, no `DROP`; violates
I-19/I-20/I-21 and is a D-1 episode. NO FIX in this round; diagnosis only.

## Local reproduction (candidate-driven, closed loop)

Scenario `scenario_r5_two_worker_banking` (make_banana_traces.py, round-5
section): banana-eligible corridor map `R5_MAP` (no water, orchard geometry
None), tent (1,1), walkable doors (2,1) and (1,2), live diagonal banana
mother on (2,2) — the single articulation cell between the east corridor and
both doors. Resident starter u0 on the (2,1) door (banana phase Active at
turn 1, mother protected); second economy worker u2 at (6,2) carrying
`[0,0,0,0,0,2]`; far opponent harvester u5 at (12,2) (I-7 never flips).

Observed on the real 9f5ef833 binary (40 turns):

```
t 3  u2=(4,2) carry=[0,0,0,0,0,2]  MOVE 2 3 2
t 4  u2=(3,2) carry=[0,0,0,0,0,2]  MOVE 2 4 2
t 5  u2=(4,2) carry=[0,0,0,0,0,2]  MOVE 2 3 2
...  (period-2 forever)
t40  u2=(3,2) carry=[0,0,0,0,0,2]  MOVE 2 4 2
```

38 alternating states, turns 3-40, cells `(4,2)<->(3,2)`, cargo unchanged,
zero `DROP` — the host episode class (same signature: two adjacent cells,
alternating `MOVE 2 a b`, full wood cargo). The episode is a stable fixed
cycle: nothing in the state can change (mother protected from every
non-resident verb, ownership never flips, cargo not droppable), so it runs
to the horizon exactly as the host's 225-turn episode ran to t258.

## First divergence (parent vs candidate, same transcript)

Parent replayed OPEN-LOOP on the candidate's own R-5 transcript (identical
per-turn states):

- t1-t3 (u0 slot): parent sends u0 to chop the (unprotected, to it) banana
  tree; candidate holds u0 as the reserved banana resident (`WAIT`) —
  expected activation divergence, not the defect;
- **t4, u2 slot — the defect divergence**: state u2=(3,2), full cargo;
  parent emits `MOVE 2 2 2` (steps onto (2,2), the unique next cell toward
  either door); candidate emits `MOVE 2 4 2` (steps backward). Every
  following even turn repeats the displacement.

Parent CLOSED-LOOP on the same scenario banks at t10 (`DROP 2` on the (2,1)
door; own wood inventory credited). Candidate never banks.

## Mechanism (hypothesis probes H1 -> H3, in order)

**H1 — I6 retain-filter removes the Bank/DROP candidate: REFUTED.**
The I6 insertion (banana_blocks/block-i6.rs, lines 13-20; readable
research-banana-r2.rs line 2092-2094) retains away candidates with
`Target::Tree(cell) | Target::Bank(cell) | Target::Cell(cell)` equal to the
protected cell. `Target::Bank` cells are the tent's ORTHOGONAL doors
(MoisanBot::bank_candidates, research lines 516-550), while the protected
mother is diagonal-only by construction (`banana_mother_cell`,
block-i1.rs lines 175-182: `!is_adjacent(cell, tent)` filter), so a Bank
candidate can never equal the mother; a full carrier's candidate list is
WAIT + Bank only (main_candidates, research lines 1719-1722). Empirical
probe: a scratch copy with the I6 retain statement deleted still oscillates
identically (probe `probe_noI6`, below).

**H2 — door-occupancy tie-flapping: CONTRIBUTING GEOMETRY, NOT THE CAUSE.**
The reserved resident standing on the (2,1) door removes that door's Bank
candidate for the carrier (YamoBot::bank_candidates occupied-door filter,
research lines 1342-1356), steering it to door (1,2); the chosen door is
STABLE across turns (no per-turn tie flip of the candidate set or scores).
With the forbidden set neutralized (probe below) the carrier banks even
with the resident camped on (2,1).

**H3 — the banana wrapper's per-turn post-edit displaces the carrier's
committed action: CONFIRMED. This is the defect.**

Exact code path, per turn of the episode (all in the I1 insertion,
banana_blocks/block-i1.rs, inside `impl Bot for BananaBot::commands`):

1. block-i1.rs lines 771-775: the wrapper writes
   `banana_protected_cell = banana_mother_cell(view)` = `(2,2)`.
2. The inner YamoBot plans the full carrier's bank route:
   `main_candidates` -> `bank_candidates` (`Target::Bank((1,2))`,
   `MOVE 2 1 2`), `MoisanBot::select`, then
   `MoisanBot::resolve_move_conflicts` REWRITES the accepted move to its
   one-step landing (research line 1015):
   - from (4,2): landing (3,2) -> `MOVE 2 3 2`;
   - from (3,2): landing = `next_cell((3,2) -> (1,2))` = **(2,2)**, the
     mother (articulation cell; unique min by `(dist, cell)`), ->
     `MOVE 2 2 2`.
3. block-i1.rs line 799: `replace_action` swaps in the resident's banana
   action (`WAIT`) — no effect on u2.
4. **block-i1.rs lines 830-836 (C5 "third protection layer")**:
   ```rust
   let banana_forbidden: BTreeSet<Cell> = mother.into_iter().collect();
   MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(
       view, &mut commands, &BTreeSet::from([worker_id]), &banana_forbidden);
   ```
   This re-resolution re-parses the ALREADY-REWRITTEN move (target = the
   one-step landing), and for the non-priority carrier applies
   `landing_forbidden` (research lines 1011-1012): landing (2,2) is
   forbidden, so the detour branch (research lines 1018-1041) picks the
   only legal ortho neighbor of (3,2) — **(4,2), the cell the carrier just
   came from** — and emits `MOVE 2 4 2`.

Why the alternation is stable (the "tie-flap" analysis): there is no score
tie inside any candidate list — the flip is the parity alternation between
the resolver's two branches. At mother-distance 2 the landing is the
distance-1 cell (never forbidden) -> accepted, carrier advances. At
mother-distance 1 the landing is the mother itself (always forbidden,
because the mother is the unique BFS-min next cell — an articulation cell
on every door route) -> detoured to the unique free neighbor, which is the
distance-2 cell just vacated. The two turn-types alternate with the
carrier's parity forever: `MOVE 2 3 2` (landing-rewrite accept) and
`MOVE 2 4 2` (forbidden-landing detour). No exit exists: the mother cannot
fall (second-layer post-edit WAITs every non-resident harming verb,
block-i1.rs lines 810-827; the resident never chops an owned mother), the
cargo cannot be dropped (both doors are behind the forbidden cell), and
I-7 never flips (opponent far). The wrapper thus converts the protected
mother from "landing-forbidden" into "transit-impossible", and the inner
policy — which re-plans the same shortest bank route every turn — never
learns that the route is administratively blocked.

## Probes (scratch-only experiments on copies of the 9f5ef833 bytes)

| probe | change (scratch copy only) | result |
|---|---|---|
| `probe_noforbid` | `banana_forbidden = mother.into_iter().collect()` -> `BTreeSet::new()` (1 site) | carrier crosses (2,2) at t5, `DROP 2` at t6, wood banked — episode gone |
| `probe_noI6` | I6 banana retain statement deleted | alternation unchanged (t3-t40) — I6 not causal |
| parent a8eb3b2b | no banana wrapper at all | closed-loop banks t10; open-loop emits `MOVE 2 2 2` at every candidate detour turn |

## Geometry iteration log (every geometry tried)

| # | map row1/row2 variant | observed |
|---|---|---|
| v0 | `#0############` / corridor (accidental: no (2,1) door) | starter cell not walkable -> activation checkpoint fails -> banana INACTIVE; carrier banks through (2,2) at t6. Shows activation is necessary for the defect. |
| v1 | `#0.###########` / `#............1` (**committed `R5_MAP`**) | REPRODUCED: period-2 `(4,2)<->(3,2)`, turns 3-40, full cargo, no DROP |
| v2 | `#0..##########` (opens (3,1): alternate door path exists, mother NOT an articulation point) | still traps: period-2 `(3,2)<->(3,1)` — detour to (3,1), then the (2,1) door landing is reserved by the camped resident, detour back. The class is broader than pure articulation geometry: forbidden-landing + door occupancy jointly suffice. |

## Host-state mapping

The host map around seed 9,854,000's tent evidently places a protected
mother so that worker 2's bank route repeatedly lands on it; the episode's
`MOVE 2 8 3` / `MOVE 2 8 4` pair is the same accept/detour parity cycle
(the final `t258: MOVE 2 8 5` marks the first turn the protection
disengaged). The local scenario reproduces the CLASS exactly
(candidate-driven, full-cargo, >= 6-turn two-cell alternation, no DROP);
the specific host cells/turn numbers are functions of the unavailable host
map bytes and were not replicated (and per instructions not fabricated).

## Gate

`regression_tests.py r5-bin` (R-5 "two-worker-full-cargo-banking") runs the
scenario closed-loop against any candidate binary and FAILs on the current
9f5ef833 bytes (episode + bounded-horizon violations); the scripted
compliant control (`control-r5-compliant`, banks at t6) proves PASS
reachable, and `control-r5-oscillator` proves the FAIL direction
non-vacuous. See red-evidence-9f5ef833-2026-08-05.md.
