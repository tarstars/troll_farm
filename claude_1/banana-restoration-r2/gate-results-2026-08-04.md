# Gate results — candidate-banana-r2 (2026-08-04)

Candidate: `claude_1/banana-restoration-r2/candidate-banana-r2.min.rs`,
74,725 bytes, sha256 `f29efd0e9c8cd17a2151678b2b0a449baba76aa12ede283d5ef486f5a5fe6eb9`.
Parent: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`,
62,725 bytes, sha256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` (verified).
Implements invariant-spec-2026-08-04.md **as revised** (commit `2696ff07`, integrator review
20260804T194501Z) — all eight corrections C1–C8 are in the shipped code (mapping in section 7).
No instrument (semantic_harness.py, trace_detectors.py, tier-p-golden.json) was modified.

## 1. Build asserts (build_banana_candidate.py) — ALL PASS

Six insertions I1..I6 per the revised seam (I2/I3 extended with
`banana_protected_cell`, new I6 retain-filter; anchors identical to the seam report):

| # | anchor (unique in parent) | mode | inserted bytes |
|---|---|---|---|
| I1 | `pub struct SecureOrchardBot{` | before | 11,554 |
| I2 | `external_protected_tree:Option<Cell>,}` | inside, before `}` | 64 |
| I3 | `external_protected_tree:None,}}` | inside, after first `,` | 49 |
| I4 | `if let Some(id)=self.external_idle_unit{...wait()]);}` | after | 80 |
| I5 | `else{return;};let mut bot=SecureOrchardBot::new();` | after | 67 |
| I6 | external_protected_tree retain statement (revised-seam bytes) | after | 186 |

Asserted mechanically on every build: parent sha256 == frozen value; per block
`compact(readable block) == inserted string` (and for I2/I3/I4/I6 additionally
`== the revised-seam-fixed exact bytes`); every anchor count == 1 in parent; every inserted
string count == 0 in parent and == 1 in output; inserted strings pairwise non-substring;
**inverse check: sha256(output minus the six insertions) == parent sha256**. Readable blocks
with full commentary: `banana_blocks/block-i1.rs .. block-i6.rs`.

Seam-delta decision recorded per risk R2: I5 is
`let _=&mut bot;let mut bot=crate::bot::moisan::BananaBot::new(bot);` — the no-op `&mut`
borrow keeps the first binding's `mut` used, so no `#[allow(unused_mut)]` attribute is needed
and the build is warning-free (below). Decided once, recorded here.

## 2. Compile gate — PASS

- `rustc --edition=2021 -O -Awarnings` → exit 0.
- Stricter than required: **without** `-Awarnings` → 0 warnings (parent baseline also 0).
- Empty stdin → exit 0, zero bytes of output, empty stderr.

## 3. TIER-P (parent-equality on dormancy fixtures) — 7/7 BYTE-EQUAL

Candidate run through the identical TIER-P recorder and diffed line-for-line +
stdout-sha against `tier-p-golden.json`:

p_baseline_plain, p_orchard_eligible, p_banana_inventory_dormant, p_wood_banking,
p_two_worker, p_late_window, p_training — **all byte-equal** (MSG banner included).
The harness's own dormancy asserts (zero BANANA-token commands, well-formed arities,
double-run determinism) passed on every fixture.

## 4. TIER-C — 8/8 PASS (`tier-c-results-2026-08-04.json`)

| fixture | verdict | notes |
|---|---|---|
| c_bootstrap_budget | PASS | single-worker payload byte-equals parent; no non-starter PICK (starter off-ring → dormant, 0 pick events) |
| c_bounded_placement | PASS | 0 plants at all 5 non-ring positions; full-ring: no PICK/PLANT; control (0,2): 30 plants, control (2,1): 0 (mother-founding routes the seed diagonally — permitted, recorded, see 8.5) |
| c_replant_renewable | PASS | **discriminator flip vs parent smoke (was FAIL)** — PLANT BANANA in the turn-50..55 window; surplus carrier approaches door |
| c_late_conversion | PASS | (a) tail = 5×CHOP, 0 HARVEST; (b) plant_turns empty (vacuous, see 8.5); (c) mother_guard **PASS** — **discriminator flip (was INCONCLUSIVE_NO_PLANT)**: candidate plants the diagonal mother, then only HARVESTs it |
| c_banking | PASS | door carrier resolves via PLANT within A=6; far full carrier emits door-approach MOVE |
| c_eta_suppression | PASS | 0 plants under opponent chopper ETA<=2; funding payload byte-equals p_training golden |
| c_arbitration | PASS | byte-equal on p_orchard_eligible + p_baseline_plain; TRAIN parity (turn 1, `TRAIN 3 3 0 3`); ≤1 harvest/turn, distinct MOVE dests, no consecutive move-onto-peer |
| c_target_recovery | PASS | definite non-WAIT within 3 turns of destruction, no period-2 alternation; 0 moves onto working peer |

## 5. Detector gate (D-1..D-9) on closed-loop banana-active traces — ALL PASS

The open-loop harness cannot exercise executed effects, so `make_banana_traces.py` drives the
compiled candidate closed-loop with a Python mini-referee (MOVE/HARVEST/CHOP/PLANT/PICK/DROP
applied per game::rules constants, plant growth each turn; opponents static). Traces, command
streams and reports under `traces/` (library reports `*-detectors.json`, byte-identical CLI
runs `*-detectors-cli.json` via `trace_detectors.py --transcript-file --commands-file`).

| trace | turns | content | D-1 | D-2 | D-3 | D-4 | D-5 | D-6 | D-7 | D-8 | D-9 | overall |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| t1_lifecycle | 300 | bootstrap PICK (1), mother founding, 21 plants (last turn 281 ≤ T_late 282), 22 harvests, 113 chops, 20 door DROPs, final bank 38 wood + 3 bananas | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |
| t2_contested | 60 | I-10a/C7: opponent harvester at ETA ≤ resident ETA from turn 1 — resident moves straight to the mother (turns 1–3), harvests immediately (4–5), then replants orth slots and cycles | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS |

D-1 scope note: in banana-active states the only commanded worker is the resident (the inert
trained peer emits WAIT), so every D-1-eligible unit in these traces is banana-attributable;
D-1 = 0 episodes on both. Parent-inherited oscillation of non-banana workers (packet games)
remains out of scope per the task instruction.

## 6. Byte budget — PASS

74,725 < 100,000 (headroom 25,275 bytes). Manifest: `candidate-banana-r2-manifest.json`.

## 7. Integrator corrections C1–C8 — implementation mapping

1. **Resident = starter**: activation binds `banana_worker` to the min-id own unit; no
   non-starter selection exists anywhere in the block.
2. **Pre-delegation arbitration**: `banana_orchard_geometry(view)` is a read-only,
   gate-for-gate replica of `SecureOrchardBot::initialize`'s geometry test (≥2 sorted doors,
   non-empty naturals, all door-reachable, `SecureOrchardBot::median ≥ 8.0`, plant-free
   water-adjacent door with enemy door distance ≥ 11), evaluated at the top of turn 1 before
   the first delegated call; no post-delegation field inspection. Post-edits happen only when
   the banana feature is enabled and Active (attribution-clean; I-27 evidence = command
   streams: byte-equality on apple/dormant fixtures, section 3/4).
3. **Single mother**: diagonal plants are eligible only while no live diagonal banana exists
   (`banana_vacant_ok` diag_taken guard); protected set = the single minimal live diagonal
   banana cell (`banana_mother_cell`).
4. **Resident ETA ownership**: plant-time safety and the contested test both use the
   resident's ETA (never a min over workers).
5. **Protection seam**: `banana_protected_cell:Option<Cell>` field/init/retain (I2/I3/I6),
   written before every delegation, None on every dormant turn; plus the post-edit WAIT
   rewrite of non-resident CHOP/HARVEST on the mother and the resolver forbidden set —
   protection is never claimed from `banana_idle_unit` alone.
6. **Hysteresis literal**: clauses 1–4 of section (e) implemented exactly (H=3 hold with no
   exceptions, eps=1 upgrade margin, strict total order (score, kind ordinal, cell), 2-turn
   block invalidation, definite command in every active mode); acceptance rests on the
   detector runs of section 5, not the (withdrawn) acyclicity argument.
7. **Ownership-loss response**: deterministic pure function of `S_t` — if the mother is
   contested and a fruit is harvestable now, forced harvest-now (move/harvest), wood
   commitment (I-19) still dominating; otherwise no further investment (see 8.2).
8. **Single-door serialization**: resident is the resolver priority unit; with one reachable
   door the DROP cell serializes by construction. The ascending-id clause is vacuous on this
   parent (max two own workers, `can_train` stops at n ≥ 2) — inherited resolver order kept.

## 8. Documented notes / residual items for the orchestrator (none failing)

1. **I-16 disjunct**: activation strictly requires ≥ 2 own units; the "training permanently
   infeasible" alternative is never exploited. This is a conservative strengthening of a
   necessary condition (no invariant violated); exploiting it would also break the
   p_late_window TIER-P golden (single worker, banked bananas, 105 turns, dormant).
2. **I-10a convert branch**: for the diagonal mother, "convert" (chop) is unreachable — I-14
   and D-8 (threshold 0, any turn incl. endgame) forbid chopping diagonal mothers, so the
   implemented response is harvest-now when ready, else no further investment (abandon);
   orthogonal wood slots bear no fruit before size 4 under the R2 cut-at-size-2 cycle, so
   fruit-ownership loss on them does not arise. Spec tension I-10a-vs-I-14 flagged for the
   next spec pass; nothing in the harness/detectors encodes the convert branch.
3. **I-3 vs I-2 interplay**: once the single bootstrap PICK is spent, a *banked* seed is
   unusable (I-2 dominates I-3's "carried or banked" clause). Mitigated by the
   mother-founding priority (below): the bootstrap seed founds the renewable diagonal mother
   first, so later seeds have harvest provenance.
4. **Mother-founding priority** (implementation of I-3 mother floor / B1): while no diagonal
   mother is alive, a Plant candidate for a diagonal vacancy scores above any orthogonal
   plant (9,000-class vs 8,800). Without it the closed-loop lifecycle strands (bootstrap seed
   dies as a wood tree — observed in the first t1 run and fixed).
5. **Fixture drift vs revised spec — none failing, three vacuous/behavioral notes**:
   (i) c_replant_renewable scripts *two* diagonal mothers (pre-revision multi-mother state);
   the candidate protects only the minimal cell (0,0) and the fixture still PASSes.
   (ii) c_late_conversion(b) and the c_bounded (2,1) / c_eta control payloads now record zero
   plants: with no live mother the seed is routed to a diagonal cell, which the open-loop
   scripted unit never reaches — assertions pass (vacuously where applicable).
   (iii) D-6's A7 min-own-ETA reading is implied by the revised resident-ETA rule
   (resident ETA ≥ min own ETA), so the detector needed no change and passes.
6. **Replay-gate items** stay with `local_codex_1` per seam R8: broad dormant-equality panel,
   banana-live replays (check 3), host-only gate on game 897829265 (check 6). The harness
   report's closed-loop gaps (I-11, D-6(b), full D-7 ledger, I-20 positional monotonicity)
   are covered locally by the section-5 closed-loop traces.
7. tier-p-golden.json is byte-identical to its committed state (harness reruns regenerate
   only the parent-path metadata; reverted each time).
