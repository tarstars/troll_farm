# Diagnosis R-6 — fuzz-panel violation families (a)-(d), round 6 (diagnosis only, NO code changes)

Date: 2026-08-06
Candidate: `claude_1/banana-restoration-r2/candidate-banana-r2.min.rs`, SHA-256
`47c98f5354ec89ea032c425394287ee24955c75846690d3527ee60ee2d167834` (verified against the
committed file before analysis).
Parent: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
(`a8eb3b2b...`).
Inputs: `fuzz/fuzz-report-47c98f53-2026-08-05.md` (+`.json`), the 156 saved game dirs under
`fuzz/failures/`, `banana_blocks/block-i1.rs` (readable form; line numbers below are that
file's), `invariant-spec-2026-08-04.md`, `diagnosis-r5-2026-08-05.md`, `trace_detectors.py`.
Method: per-family sampling of 4-19 saved games (map spec + both transcripts + both command
streams), byte-level candidate-vs-parent command diffing (`cmp`/`diff` on the committed
per-game streams — the saved parent stream IS the paired differential run, so no re-run was
needed to find first divergences), and per-turn state reconstruction from the transcripts.
All sources read-only; only this file and scratchpad were written.

**Headline: the four provisional clusters re-factor into FOUR confirmed roots, with
different boundaries than the provisional clustering.** Family (a) is not a candidate
defect at all (detector attribution gap over inherited parent behavior, and it also absorbs
an inherited slice of (c) and of the D-4 list). Families (b) and (d) share one super-root —
"the wrapper parks the resident" — expressed as route blockade (b), banking bounce (b/D-1),
and reservation starvation (d). Family (c) is the ownership/safety model, whose branch-3
outcome *feeds* (d) and whose released cell claim feeds the candidate D-8 episodes.

---

## Family (a) — P1/D-9 "solo banana activation" (74 games)

### 1. Evidence

Nineteen of the D-9 games sampled: m001-s0/s1, m010-s0, m011-s1, m016-s0, m020-s1,
m029-s0, m033-s0, m034-s0, m037-s0, m038-s0, m043-s0, m044-s0, m048-s1, m051-s0, m053-s1,
m054-s0, m057-s1, m062-s0, m067-s0. **In every single one the candidate command stream is
byte-identical to the parent stream on the same map/seat**
(`cmp fuzz/failures/<g>/candidate-commands.txt fuzz/failures/<g>/parent-commands.txt`
returns equal for all 19). Exemplar windows: m001-s0 turns 82-83 (`DROP 0` / `PICK 0
BANANA` / `PLANT 0 BANANA` — identical in `parent-commands.txt` lines 81-83), m016-s0
t11-12 and t99-100, m044-s0 t128-135, m053-s1 t63-70.

Common preconditions: maps whose starting roster is a **single own worker for the whole
game** (m001-s0 transcript: own = unit 0 only, opponent = unit 5, all 200 turns), no TRAIN
ever emitted by either bot, all map classes and all three opponent profiles. The banana
verbs are the parent's inherited `yamo-carry-regen-transit-idle-harvest` regeneration
cycle: after clearing a cell it PICKs a banked resource and replants it (`PICK 0 BANANA;
PLANT 0 BANANA` at t82-83 is followed at t88-89 by `PICK 0 LEMON; PLANT 0 LEMON` — same
loop, different crop).

### 2. Mechanism

There is **no block-i1 code path involved**. The activation gate
(block-i1.rs 694-716) is correct for these games and never fires:

```rust
// I-16: activation requires the trained second worker.
let mut own: Vec<&Unit> = ... .filter(|unit| unit.player == 0).collect();
if own.len() < 2 { return; }
```

With one own unit the phase stays `Dormant`, `active == false`, `lost_hold == false`, and
`commands` is returned untouched (block-i1.rs 776-779, the structural identity) — which is
exactly what the byte-identical streams show. There is no missing second-worker/funding
precondition in the gate; I-16's `|own units| >= 2` is enforced. (The gate does omit
I-16's alternative arm "or training permanently infeasible (`300 - t <= 20`)" — that
omission only makes activation *stricter*, never earlier, so it cannot produce D-9.)

The violation is manufactured by the detector. `trace_detectors.py` `detect_d9`
(lines 1173-1224) flags **any** `PLANT/PICK ... BANANA` while `|own units| == 1` before
the first own TRAIN, per its assumption A10 (lines 68-73): *"D-9 literal reading: any
banana-attributable command (PLANT ... BANANA or PICK ... BANANA) ..."*. A10
over-approximates "banana-attributable" (spec D-9, invariant-spec line 411) to the
verb+resource pair. But spec I-18 (line 253-255) defines the compliance condition for
exactly this phase: *"before that, funding-phase commands are **byte-equal to the parent**
(check 4 makes this the default)"* — and these games ARE byte-equal. A command the parent
emits identically on the identical state cannot be banana-attributable; the wrapper was
provably inert.

The same non-differential application of P1 detectors also mis-attributes an inherited
slice of other families: m038-s1 and m048-s0 (D-6 `opp_chop_eta`) and m064-s0 (D-4
`no_progress`) are **also byte-identical to the parent** yet counted as candidate
violations.

### 3. Root

**ROOT A — detector/panel attribution gap**: the fuzz panel applies D-9's
`banana_before_train` clause (and D-4/D-6 generally) to the raw candidate stream without
the parent-differential gate that D-1 already has (the report's "inherited-parent-D1"
report-tier). 74 D-9 games (69 of them with no other detector), plus at least 3
inherited D-6/D-4 games, are parent behavior.

### 4. Minimal fix proposal

- **Change**: in `trace_detectors.py`/fuzz panel, gate the `banana_before_train` episode
  (and, for symmetry, D-4/D-6 episodes) on divergence: emit the episode only if the
  flagged command slot differs from the parent's aligned command on the identical map/seat
  (the paired stream is already an input of D-9's TRAIN-parity clauses). No block-i1
  change; **zero candidate bytes change**.
- **Invariant text**: revision-block amending A10: "banana-attributable = a command not
  byte-equal to the stable parent's command for the same unit-slot on the paired replay"
  (this is I-18's own definition of the compliant default, so the spec's D-9 text needs no
  change — only A10's reading).
- **Blast radius**: none on R-1..R-5, TIER, or t1-t6 (candidate untouched). The detector
  self-test (`detector-selftest-report-2026-08-04.md` fixtures) needs one new paired
  fixture (inherited-replant, must NOT flag) and keeps the existing positive fixture (a
  wrapper-emitted pre-TRAIN PICK with a diverging parent slot, must flag).
- **Expected panel**: the 69 pure-D-9 blocking games unblock; D-9 count 74 -> 0 unless a
  genuinely diverging pre-TRAIN banana verb exists (none found in 19/19 samples);
  m038-s1/m048-s0/m064-s0 drop their inherited episodes.

### 5. GREEN witnesses

Re-run detectors on saved streams (no game re-run needed): m001-s0, m016-s0, m044-s0,
m053-s1 (expect D-9 = 0 each); negative control: hand-edited copy of m001-s0
candidate stream with the parent slot changed to `WAIT` (expect D-9 fires) — scratch only.

---

## Family (b) — P2 full-cargo alternation (8) + candidate-only D-1 oscillation (29)

### 1. Evidence

Sub-family **(b1) — full-wood carrier livelocked behind the WAIT-camping resident** (all 8
P2 games sampled 5): m066-s0 (unit 2, `(4,2)<->(3,2)`, t4-29, carry `[0,0,0,0,0,2]`),
m042-s1 (`(8,2)<->(7,2)`, t16-29), m030-s1 (`(8,3)<->(9,3)`, t18-37, then follow-on D-1
runs to t200), m050-s1 (`(7,2)<->(8,2)`, t3-12), m056-s1 (`(5,2)<->(6,2)`, t17-29).
Common preconditions verified in each transcript: two own workers; wrapper Active; the
diagonal mother planted on the ring (m066: (2,2); m042-s1: (9,2); m030-s1: (10,3);
m056-s1: (7,2)); **the resident standing motionless ON the mother cell for the whole
window** (m066: resident WAITs on (2,2) t4-26; m042-s1: WAITs on (9,2) t12-26; m030-s1:
WAITs on (10,3) t18-37; m056-s1: WAITs on (7,2) t17-29); the carrier's one-step landing
toward its bank door equals that cell. The episode ends exactly when the mother state
changes and the resident finally moves (m066: `HARVEST 0` at t27, resident leaves, unit 2
banks t31).

Sub-family **(b2) — the RESIDENT bouncing on its own banking run** : m023-s0 (unit 0,
`(1,2)<->(0,2)`, t7-200, k=96, carrying 1 wood from the convert chop; also the P4 stall of
that game). Unit 2 is parked by the inner policy on door (2,2) from t3 to t200.

Sub-family **(b3) — inherited inner-policy oscillation on divergent state**: m007-s0
(unit 0, `(2,4)<->(3,4)`, t165-200): at t165 the banana phase is long Abandoned (only
surviving plant is the opponent-side APPLE (11,4); no live ring banana, bootstrap spent,
`banana_lost` never set — idle opponent), so unit 0 is inner-controlled; it bounces around
own unit 2 parked at (4,4). Same class as the 24 report-tier "inherited-parent-D1" games —
candidate-only merely because the candidate's history parked unit 2 elsewhere. m017-s0/s1
match this shape (late windows, no wrapper involvement).

### 2. Mechanism

**First divergence (paired streams, m066-s0)**: candidate t1 `PICK 0 BANANA` vs parent t1
`MOVE 0 2 2` (activation divergence, expected). The defect-relevant divergence: the parent
oscillates unit 2 too (`(4,2)<->(5,2)`, t3-22) while its unit 0 CHOPs at (3,2) — the
inherited "corridor blocked by own busy unit" pattern, **bounded by the chop's completion
(t22)**; the candidate's identical pattern is bounded only by the mother's first fruit
(t27) or, on other maps, by nothing at all. The r5 mechanism (forbidden-set landing veto)
is gone — the current trigger is *physical occupancy*.

Causal chain, per turn of a (b1) episode:

1. block-i1.rs 769-770 reserves the resident: `banana_idle_unit = worker`; the inner
   plans WAIT for it (block-i4.rs). banana_action's candidate set while standing on a
   fruitless live mother is `[WAIT]` only — block-i1.rs 349:
   `let mut out = vec![(0, BananaTask::Idle, worker.cell, "WAIT".to_string())];`
   (no chop for a diagonal mother, no harvest while `fruits == 0`, no Plant without a
   carried seed, bootstrap spent, nothing carried to bank). **There is no step-aside/idle
   placement logic anywhere in the file** — Idle always camps `worker.cell`, which is the
   mother, for the entire growth window.
2. The inner resolves the carrier's bank route and rewrites the accepted move to its
   one-step landing; on these geometries the landing is the camped cell.
3. block-i1.rs 843-847 re-resolves:
   `MoisanBot::resolve_move_conflicts_with_priority(view, &mut commands,
   &BTreeSet::from([worker_id]))`. Inside the resolver (candidate min.rs,
   `resolve_move_conflicts_with_priority_and_forbidden`): `reserved` is initialized with
   the cells of all **non-moving own units** — the WAIT-camping resident's cell is
   permanently reserved; the carrier's landing hits `reserved.contains(&landing)` and
   falls to the detour branch, `min_by_key |cell| (toward_goal.get(cell), *cell)` over the
   free ortho neighbors. In a corridor the only free neighbor is the cell just vacated
   (m066: from (3,2), neighbor (2,2) reserved -> detour (4,2)); on open maps all free
   neighbors tie on distance-to-landing and the **lexicographic tie-break picks the
   backward/min cell** (m042-s1: from (8,2), landing (9,2) reserved; (7,2),(8,1),(8,3)
   all dist 2 -> `(7,2)` = min cell). Next turn the inner re-plans the same shortest
   route -> accept -> parity loop. This is diagnosis-r5's accept/detour cycle with
   `reserved` in place of the removed `landing_forbidden`; note r5's own probe v2 already
   showed "forbidden-landing + door occupancy jointly suffice" — the r5 fix removed only
   the first conjunct.
4. Nothing exits the loop: the resident has no reason to move (WAIT is its only
   candidate), priority is irrelevant against a *stationary* blocker, and the carrier's
   commitment is re-planned identically every turn.

**(b2) mechanism** (m023-s0, resident side): after the t4-6 convert chop (see family (c))
the resident carries 1 wood; block-i1.rs 351-353 short-circuits to bank-only candidates.
`banana_bank` (289-312) offers **every walkable door, with no occupancy filter** — unlike
the inner policy's own `bank_candidates` occupied-door filter (cited in diagnosis-r5 H2).
From (1,2) the doors (1,3) and (2,2) tie at eta 1, and the selection
`max_by_key (score, kind, cell)` (block-i1.rs 641-642/666-667) breaks the tie toward the
**larger cell — (2,2), the door occupied by parked unit 2**. The resolver then reserves
(2,2) (stationary unit) and detours the resident to the lexicographic-min free neighbor
(0,2) (neighbors (0,2)/(1,1)/(1,3) all dist 2 to (2,2) -> (0,2)); next turn the wrapper
re-emits toward (2,2) from (0,2) via (1,2)... period-2 forever. The commitment machinery
never breaks it because the blocked-turn counter (block-i1.rs 481-482)
`let stalled = self.banana_last_move && self.banana_last_cell == Some(worker.cell);`
only counts turns where the position did NOT change — a two-cell bounce changes position
every turn, so `banana_blocked_turns` stays 0 and clause-1 invalidation never fires.

**(b3)** involves no wrapper code path at all on the violating turns (phase Abandoned,
`lost_hold` false, structural identity); it is the inherited inner oscillation class
surfacing on candidate-divergent unit placement.

### 3. Root

**ROOT B — stationary-resident route blockade at the C8 seam** (b1+b2 and the early k=3
D-1/D-4 bounces in m021-s0/s1, m024-s0, m026-s1, m066-s1 — same resolver-detour signature
at sub-livelock scale): the wrapper parks the resident (Idle camps `worker.cell`; lost/
frozen states, family (d), park it too), the parked cell is `reserved` in the C8
re-resolution, and the detour tie-break converts a blocked one-step landing into a stable
parity cycle. Plus the (b2)-specific aggravations: no occupied-door filter in
`banana_bank` and a bounce-blind blocked counter. (b3) splits OUT of the family into the
inherited report-tier class.

### 4. Minimal fix proposal

Three small changes in block-i1.rs, all active-path only:

- **F-B1 idle-yield**: in `banana_action`, when the chosen candidate is
  `(Idle, worker.cell)` and any other own unit with `total_carried() > 0` is within
  Chebyshev distance 2 (deterministic), emit a step-aside `MOVE` to the min free walkable
  ortho neighbor of `worker.cell` instead of WAIT (fall back to WAIT if none). The mother
  needs no occupancy — every protection layer (I6 retain filter, second-layer post-edit)
  is cell-based, and the resident re-approaches at eta 1 when fruits ripen.
- **F-B2 occupied-door filter in `banana_bank`**: skip a door whose cell holds another
  own unit (mirror of the inner's own filter and of `banana_vacant_ok`'s occupancy
  check); keep it as MOVE target only if no free door exists.
- **F-B3 progress-based blocked counter**: count a turn as blocked when the BFS distance
  from `worker.cell` to the held target did not decrease (covers bounces), so clause-1's
  2-blocked-turn recompute fires and hysteresis can re-target.
- **Invariant text**: none required (I-19/I-20/I-21 already forbid the behavior); optional
  clarification to C8/I-27: "resident priority applies to movement conflicts; an idle
  resident must not be a persistent stationary obstacle on a teammate's committed bank
  route".
- **Blast radius**: dormant identity untouched (t1-t6 safe). R-5 stays green (its
  scenario's carrier is unblocked with or without an idle resident on the (2,1) door;
  F-B1 makes the resident step aside, which R-5 does not forbid). R-2/R-3/R-4 don't
  exercise idle turns near carriers. TIER: re-run; command changes only on turns where
  the resident previously WAITed adjacent to a loaded teammate.
- **Expected panel**: all 8 P2 games vanish; corridor D-1s (m030-s1, m026-s0's t41-148
  run, m050-s0's t41-100 run, m059-s0) and the early k=3 D-1/D-4 bounces collapse;
  m023-s0's k=96 D-1 vanishes via F-B2/F-B3. The (b3) inherited-class D-1s (m007, m017)
  are NOT promised by these fixes — they should be re-tagged report-tier by the ROOT A
  differential gate logic applied to D-1's inherited check on the diverged-state
  definition, or accepted as inherited.

### 5. GREEN witnesses

Re-run saved maps: m066-s0 (unit 2 DROPs within ~7 turns of full cargo; no 26-state
alternation), m042-s1, m030-s1, m056-s1, m050-s1 (P2 gone), m023-s0 (`DROP 0` lands;
D-1 k=96 gone), m021-s0/m024-s0 (k=3 episodes gone). Regression: R-5 binary check must
stay PASS; m066-s1 D-4 episodes gone.

---

## Family (c) — P1/D-6 opponent-favored fruit creation (29 games)

### 1. Evidence

Candidate-attributable samples (streams diverge from parent): m050-s0 (D-6
`opp_harvested_ours` x15 at mother (2,2), t39-96, opp unit 5 camps the cell from t39 to
game end; D-8 `flip_but_infeasible` by **unit 2** t39-44), m003-s0 (D-6 at mother (2,4)
t65-66; after the t42-freeze all three own-planted bananas — (1,4),(2,4) + natural (4,5)
— mature to 3 fruits and stand unharvested), m009-s0 (D-6 at own orth slot (1,3)
t100/145/190 — the half-chopped slot abandoned at t42 regrows and fruits forever),
m026-s0 (D-6 x12 at (2,5) t45-93 + unit-2 D-8), m060-s1 (D-6 x4 at (7,4)), m009-s1 (D-6
x8 at (8,2)). `opp_chop_eta` sub-kind: m015-s0 (t32, eta_opp_x 0) and m068-s0
(t171-177) are candidate-attributable; m038-s0/s1 and m048-s0 are byte-identical to the
parent (ROOT A slice).

Common preconditions: harvester (or chopper for `opp_chop_eta`) profile; mother founded
on a map where the opponent's patrol reaches the ring within a fruit cycle; the resident
is ON or adjacent to the target cell at plant time (making `eta_res` 0-1).

### 2. Mechanism

The plant decision is `banana_vacant_ok` (block-i1.rs 256-284), whose safety clause is:

```rust
Self::banana_opponent_eta(view, cell, false) > resident_eta
    && Self::banana_opponent_eta(view, cell, true) > 2
```

This is the I-7/C4 ownership test **evaluated at the plant instant with the resident's
current-position ETA** — 0 when standing on the cell, 1 when adjacent. It is satisfiable
with an opponent harvester one or two cells away (m023-s0: opp at (2,1), eta 1 > 0, PLANT
executes; the opp steps onto the mother the NEXT turn and I-7 flips — ties conceded — at
t4, one turn after founding). The check is present and uses the right actor (the
resident, per C4); **its timing horizon is wrong**: ownership per I-7 is a *continuous*
property re-evaluated every turn against a mobile opponent, while the guard certifies
only the single planting instant. A mother needs ~`2*CD + ...` turns to first fruit and
must win the ownership race at *every* fruit event; a flat `> eta_res` (= "> 0") margin
certifies none of that. The chopper clause `> 2` has the same flaw against the
conversion horizon (m015-s0: chopper arrives at eta 0 by t32; m012/m028: choppers kill
the mother 20 turns after founding with no possible response — see (d2)).

Once the flip lands, branch 2's oracle is usually infeasible exactly when the opponent is
close and a fruit is ripe (`ripe = 0`, so `feasible = eta_res + chops - 1 < eta_opp` with
`eta_opp` 0-1 — block-i1.rs 586-601), so branch 3 runs (615-623): the mother is left
**alive**, and the wrapper then *releases the cell claim* while keeping the worker
(block-i1.rs 771-775 sets `banana_protected_cell = None` once `active` is false, and
805-809 clears `mother` when `banana_lost`):

```rust
let mother = if self.banana_lost { None } else { Self::banana_mother_cell(view) };
```

Consequences on the traces: the opponent farms the standing banana every regrowth
(m050-s0 x15, m026-s0 x12, m003/m009), and the now-unprotected cell becomes a legal inner
target — the inner sends unit 2 to chop the lost mother with no oracle (m050-s0/m026-s0
D-8 `flip_but_infeasible`, unit 2), then bounces off the camping opponent forever
(the long D-1 runs of those games). The D-8 episodes flagged on THIS candidate are
therefore not the resident's convert branch at all — they are inner-policy chops enabled
by the inverted claim release. (`m003-s1`'s D-8, unit 2, same shape.)

### 3. Root

**ROOT C — ownership/safety model horizon**: (i) `banana_vacant_ok`'s plant-time margins
(`> eta_res`, `> 2`) certify an instant, not the asset's fruit/conversion horizon;
(ii) after ownership loss the claim handling is inverted — the cell claim (which
prevents own-side reinvestment, the thing I-10a's hold is FOR) is released while the
worker (which I-10a does not require holding) is retained (see ROOT D). D-6's
`opp_harvested_ours` and the candidate D-8/D-1 tails are downstream of (i)+(ii).

### 4. Minimal fix proposal

- **F-C1 founding margin**: for the *diagonal mother* only, require
  `eta_opp_h > eta_to_first_harvest` (time to first harvestable fruit from the planted
  state via `banana_predict_growth`, anchored like the oracle) and
  `eta_opp_x > conversion horizon (2*CD + ceil(health(2)/chop))` instead of the flat
  margins; keep the current cheap margins for orth wood slots (they are meant to be cut
  within one cycle). Deterministic, uses only existing helpers.
- **F-C2 persistent claim on a lost live mother**: keep `banana_protected_cell` set (and
  the I6 filter active) while a lost mother is alive; i.e. at 771-775 use
  `active || (banana_lost && mother alive)` and drop the 805-809 `banana_lost -> None`
  override for the *filter/post-edit* layers (movement stays free per r5). This stops
  inner reinvestment (D-8 unit-2 chops, the m050/m026 bounce tails) at one seam.
- **Invariant text**: revision-block on I-10a/I-29: "after the Abandoned transition the
  protected-cell claim persists while the lost plant lives (no own unit selects it as a
  target); the worker reservation does not persist" — this is the corrected reading of
  C7's 'cease all investment'.
- **Blast radius**: R-2a/R-2b and R-3 (oracle boundary) untouched — the flip decision
  logic (506-624) is not modified. R-1 (one-seed) unaffected. Fewer mothers founded on
  harvester/choke maps — TIER margins need a re-run (this is the highest-risk fix: F-C1
  trades D-6 violations for fewer banana activations; if TIER wood output regresses, the
  fallback is F-C2 + F-D1 only, which already remove the farming *persistence*).
- **Expected panel**: candidate D-6 `opp_harvested_ours` -> ~0 (mothers either not
  founded in range or defended/denied); candidate D-8 (7) -> 0 via F-C2; the D-6 tail in
  m009 (orth slot) needs F-D1 (the slot fruits only because the frozen resident never
  finishes the chop).

### 5. GREEN witnesses

m050-s0 (no D-6/D-8; either no mother at (2,2) or opponent never executes a harvest),
m003-s0, m026-s0, m060-s1, m015-s0 (`opp_chop_eta` gone), m009-s0 (with F-D1: slot (1,3)
finished or banked, D-6 gone). Regression: R-2a/R-2b/R-3a/R-3b must stay green
(unchanged code), R-1 green.

---

## Family (d) — P4 liveness stalls (24 games)

### 1. Evidence

Two disjoint sub-populations by opponent profile (JSON: 13 harvester, 9
chopper_aggressor, 2 other):

**(d1) lost-hold freeze (harvester maps)**: m009-s0 (flip at t42: opp 5 reaches (0,4),
`eta_opp = 1 = eta_res` to mother (0,3), fruits ripe so `ripe = 0` -> oracle infeasible
-> branch 3; resident frozen at (1,3) t42-199, its half-chopped slot at (1,3) abandoned
at health 3; P4 window 38-199), m009-s1 (same, window 38-199), m050-s1 (window 24-199),
m056-s0 (window 111-199), m023-s1 (window 40-199), m023-s0 (frozen *in the b2 banking
bounce*, window 7-199). In every case the resident never acts again and the inner's
second unit is structurally idle (it WAITs in the parent too once its opening chores are
done).

**(d2) Active-phase starvation (chopper/idle maps)**: m012-s0 (resident plants mother
(3,2) at t3, then emits WAIT **t4-t200**; opp choppers — `harvest_power = 0` in the unit
stats — chop the mother dead by t24; no reaction ever; P4 window 19-199), m012-s1,
m028-s0 (identical shape, window 17-199), m028-s1, m065-s1 (window 30-199).

### 2. Mechanism

**(d1)**: branch 3 (block-i1.rs 615-623) sets `banana_lost` and from then on the wrapper
holds the worker forever — block-i1.rs 761-770:

```rust
let lost_hold = self.banana_enabled == Some(true) && self.banana_lost && ...;
self.inner.inner.banana_idle_unit = if active || lost_hold { self.banana_worker } else { None };
```

with the per-turn action `banana_lost_action` (318-340) degenerating to `"WAIT"` the
moment `total_carried() == 0`. The stated rationale (88-92, 757-760: "releasing it would
let the inner policy reinvest in the opponent-owned asset") is doubly wrong on the
evidence: it idles the *wrong resource* (the worker — I-10a demands ceasing investment
in the ASSET, not ceasing all work; the worker then does nothing for 100-160 turns), and
it does NOT prevent reinvestment (other units are free precisely because the cell claim
was simultaneously released — the m050-s0 unit-2 chops). The freeze also preempts the
wood-cycle mid-chop (m009's (1,3), m050-s0's (2,1) at health 1, one chop from banking) —
the D-4 "abandoned carried-wood/no-progress" episodes co-occurring in these games are the
same freeze seen by a different detector.

**(d2)**: the flip block (506-624) can never fire because `banana_opponent_eta(view,
mother, false)` counts **harvesters only** — against a chopper-only opponent
`eta_opp = 10_000` and ownership never flips, even while the opponent is chopping the
mother on the resident's own cell (m012: mother health 3->0 under the WAITing resident).
Meanwhile the Active candidate set is `[WAIT]` for the entire mother-growth window (no
seed carried, bootstrap spent, no fruits, nothing to chop — family (b) mechanism step 1),
so the resident emits WAIT until the mother dies; then `banana_update_phase` (732-740)
goes Abandoned (not lost) and the inner gets a worker back at t~25 with the opening
economy forfeited (the parent spent t2-15 chopping the natural plum and banking). P4's
"parent progresses in the same window" is exactly that forfeited opening plus the
structurally idle second unit.

### 3. Root

**ROOT D — reservation without work**: the wrapper reserves the resident in states where
its own policy provides no productive action: permanently after ownership loss
(`lost_hold` + WAIT `banana_lost_action`), and for arbitrarily long Active windows in
which the candidate generator has literally nothing to offer (fruitless mother, no seed,
chopper-blind flip logic). (b1)'s camping is this same parked state seen by the resolver;
(d) is it seen by the liveness clock — **(b) and (d) are one super-root with two
geometries**, confirming the cross-family hypothesis in the task brief, while (d1) vs
(d2) split by which code path parks the worker.

### 4. Minimal fix proposal

- **F-D1 release the lost worker**: in the `lost_hold` path, once
  `worker.total_carried() == 0` (leftovers banked), stop reserving: clear
  `banana_idle_unit` (keep `banana_lost` latched to block re-activation, and keep the
  F-C2 persistent cell claim so the inner cannot reinvest in the lost mother). The inner
  immediately re-employs the worker (it is the parent's primary economy unit).
- **F-D2 starvation release**: in `banana_action`, when the chosen candidate is Idle for
  the 3rd consecutive turn (reuse `banana_hold_age` on the Idle target), stop writing
  `banana_idle_unit` for as long as the choice stays Idle — the inner plans real work for
  the resident; the wrapper re-asserts the reservation on the first turn a non-Idle
  candidate exists. Deterministic; the commitment state machinery is already
  re-entrant (clause 1 recompute).
- **F-D3 chopper-aware response (optional, larger)**: include choppers in the flip
  trigger (mother under `eta_opp_x <= 1` or health decreasing) so m012-class games at
  least convert/abandon instead of spectating. Can be deferred; F-D2 alone restores
  liveness there.
- **Invariant text**: same I-10a revision-block as F-C2 (worker reservation does not
  survive the Abandoned transition); note for I-22/I-23 (arbitration) that a temporarily
  released resident remains the designated banana worker.
- **Blast radius**: **R-4 (flip-response reachability) and R-2a must be re-run and are
  the risk hot-spots** — R-2a asserts the post-abandon resident "ceases investment"; with
  F-D1 the inner may route the ex-resident near the lost mother, so R-2a's assertion must
  be about banana-verbs/asset-targets (which F-C2 blocks), not about idleness. If R-2a
  literally requires idling, it needs the same revision-block. t1-t6 dormant identity
  untouched. TIER expected to IMPROVE (parent economy restored on 24 stalled games).
- **Expected panel**: all 24 P4 games vanish (candidate matches or beats parent progress
  windows); most D-4 episodes (11) vanish with them; m009's D-6 tail closes.

### 5. GREEN witnesses

m009-s0/s1 (progress resumes <= t45; slot (1,3) banked), m050-s1, m023-s1, m056-s0 (d1);
m012-s0/s1, m028-s0/s1, m065-s1 (d2; candidate banks wood in the t20-40 window like the
parent). Regressions: R-2a/R-2b, R-4 (must stay green, possibly with the amended
assertion), R-5, R-1; TIER-C re-run.

---

## Cross-family analysis (merge/split verdict)

The four provisional clusters are re-factored into four confirmed roots with moved
boundaries:

| root | families absorbed | mechanism (one line) |
|---|---|---|
| **A** detector attribution | ALL of (a); inherited slices of (c) (m038, m048) and D-4 (m064); (b3) re-tag | non-differential detectors flag byte-identical inherited parent behavior |
| **B** parked-resident blockade (super-root with D) | (b1) P2 + corridor/early D-1/D-4 bounces; (b2) m023-s0 | stationary reserved resident + C8 re-resolution detour tie-break = parity livelock; bank door choice ignores occupancy; blocked counter bounce-blind |
| **C** ownership horizon + inverted claim release | candidate slice of (c); candidate D-8 (unit-2 chops); D-1 tails of m050/m026 | instant-margin plant safety certifies nothing beyond t+1; post-loss the cell claim is dropped and the worker kept — exactly inverted |
| **D** reservation without work (super-root with B) | ALL of (d); most D-4; feeds (b1) | lost-hold idles the worker to game end; Active WAIT-starvation + chopper-blind flip idles it for the growth window |

Ordering: A is independent. C's branch-3 outcome is the entry state of D1; D's parked
worker is the obstacle of B; so the fix order that maximizes independent verification is
A -> B(F-B1..B3) -> D(F-D1,F-D2) + C(F-C2) -> C(F-C1, highest risk).

## Consolidated verification matrix (red -> green witnesses)

| fix | must flip to green | must stay green |
|---|---|---|
| F-A (detector) | m001-s0, m016-s0, m044-s0, m053-s1 (D-9=0); m038-s1, m048-s0, m064-s0 | detector self-test positives, all paired TRAIN-parity clauses |
| F-B1/B2/B3 | m066-s0, m042-s1, m030-s1, m056-s1, m050-s1 (P2); m023-s0, m021-s0, m024-s0 (D-1/D-4) | R-5 binary, t1-t6 identity, R-1 |
| F-C1/C2 | m050-s0, m003-s0, m026-s0, m060-s1 (D-6); m003-s1, m050-s0 (D-8); m015-s0 (opp_chop_eta) | R-2a/b, R-3a/b, R-4, TIER-C margins |
| F-D1/D2 | m009-s0/s1, m012-s0/s1, m028-s0/s1, m023-s1, m065-s1, m056-s0 (P4); D-4 set | R-2a (possibly amended), R-4, R-5, TIER-C |

All witnesses are committed under `claude_1/banana-restoration-r2/fuzz/failures/` and are
re-runnable deterministically via the panel's saved map specs + seeds
(`make_banana_traces.py` machinery); the family-(a) witnesses need only a detector re-run
on the saved streams.
