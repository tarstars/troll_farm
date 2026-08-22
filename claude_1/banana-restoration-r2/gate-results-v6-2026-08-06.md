# Gate results v6 — banana-restoration-r2 round-6 GREEN (four-root repair per diagnosis-r6)

Date: 2026-08-06
Task: `20260802-banana-restoration-r2`, round-6 GREEN phase: implement the four
confirmed roots of `diagnosis-r6-2026-08-06.md` under the orchestrator's rulings
(1: ROOT-A parent-differential gating in the PANEL for D-9 only; 2: roots
B/C(F-C2)/D in `banana_blocks/block-i1.rs`; 3: spec amendment + R-2a predicate;
4: F-C1 only if D-6/plant-safety persists — it did, F-C1 implemented).
Toolchain: rustc 1.97.1 `--edition=2021 -O` (no `-Awarnings`), Python 3 stdlib,
deterministic.

## Candidate

- NEW: `candidate-banana-r2.min.rs`, **80,934 bytes**, sha256
  `eac2eb36b5f2abf0e92b62615584f3d9135055a09e6eec0bbee7c4e4a6a4f23b`
- OLD (round-6 RED): 77,299 bytes, sha256
  `47c98f5354ec89ea032c425394287ee24955c75846690d3527ee60ee2d167834`
  (verified against the committed file before work began)
- Readable form regenerated: `research-banana-r2.rs`, 159,994 bytes, sha256
  `2730338b812e96c88f5d7e7732fda1c7aff6262627a36241b9914843e0d93456`

## The fixes

### ROOT A — detector attribution (fuzz_panel.py ONLY, per ruling 1)

`claude_1/pipeline/fuzz_panel.py` `eval_p1` now gates **D-9** episodes on the
parent baseline the panel already produces: an episode counts against the
candidate only if absent from `detect_d9` over the parent's own run on the
identical map/opponent; parent-reproduced episodes become report-tier
`inherited-parent-D9` flags (mirror of the existing D-1 tier).
`trace_detectors.detect_d9` is untouched — the base-detector question goes to
the integrator. Documented in the panel docstring and
`fuzz-panel-config.json` `notes`. Controls: identity gate on the committed
m001-s0 streams FAIL(2)→PASS(0); hand-edited parent slot (→WAIT) keeps FAIL.
D-9 blocking games: **74 → 0** (74 report-tier flags).

### ROOT B — parked-resident blockade (block-i1.rs)

- **F-B1 idle-yield** (revised from the diagnosis sketch on panel evidence):
  an Idle resident camping the mother with a loaded teammate within Chebyshev
  2 steps aside ONCE to the minimal free walkable ortho neighbor whose removal
  still leaves every nearby loaded teammate a BFS-reachable bank door (the
  I-15 alternate-door test with the aside cell removed — the naive
  min-free-neighbor from the diagnosis re-entered the corridor or ping-ponged
  mother↔door in-phase with the carrier's detour and kept the livelock);
  off the mother the resident holds (WAIT) instead of stepping back.
- **F-B2 occupied-door filter** in `banana_bank`: doors holding another unit
  are skipped while any free door exists (kept as MOVE targets only when no
  door is free).
- **F-B3 progress-based blocked counter**: a post-MOVE turn counts blocked
  when the BFS distance to the held target did not drop below the best
  distance achieved while holding it (`banana_best_dist`), so period-2
  bounces (position changes, no net progress) feed clause-1's 2-blocked-turn
  recompute exactly like standing still. Plus **blocked-hold**: when the
  block-triggered recompute re-elects the same target, the resident holds one
  turn (wood-free turns only — a wood-committed WAIT would trip D-4) instead
  of re-feeding the resolver's detour parity; the inserted repeat cell breaks
  any A-B-A alternation while the probe resumes when the blocker moves.

### ROOT C — ownership model (F-C2 + F-C1)

- **F-C2 persistent claim on a lost live mother**: the `banana_protected_cell`
  seam and the second-layer post-edit now persist while `banana_lost` and the
  plant lives (previously inverted: the claim was dropped, the worker kept).
  The round-6 D-8 `flip_but_infeasible` episodes were inner-policy chops of
  the released mother; they are gone (D-8: 7 → 0).
- **F-C1 founding-horizon margin** (ruling 4 evaluated: after A+B+C2+D the
  panel still blocked on candidate-attributable D-6/plant-safety findings —
  22 D-6 games at the evaluation point — so F-C1 was implemented): diagonal
  mother founding requires `eta_opp_h > CD(c) + ceil(health(2)/chop)` and
  `eta_opp_x >` the same margin (10 dry / 8 wet at chop 1); orth wood slots
  keep the old instant margins. The diagnosis's stricter first-fruit
  (`4*CD`) and conversion-horizon (`2*CD + chops`) variants were tried and
  are **bounded out by two committed normative witnesses**: R-4's founding
  must execute against a harvester at decision-time eta 11 (margins > 10
  ERROR the mandatory R-4 gate), and t1's lifecycle founding must execute
  against a static chop-capable opponent at eta 13 (chopper margins ≥ 13
  gut the committed lifecycle fixture). The implemented margin still refuses
  every witnessed farmable founding (eta_opp_h 0–5 at plant time).
  **Activation-rate note (ruling 4)**: `banana_activated_games` stays
  171/240 (metric counts any banana verb); mother foundings are refused on
  opponent-proximate maps — the flipped D-6 witnesses (m050-s0, m003-s0,
  m026-s0, m015-s0) found no mother or an undisturbed one; opponent-free
  geometries are unaffected.

### ROOT D — reservation without work (F-D1 + F-D2 + refinements)

- **F-D1**: the post-loss `lost_hold` is replaced by a `banana_lost_banking`
  latch — the resident is reserved only until the leftover cargo it carried
  AT the loss is banked, then released to the inner economy permanently.
  Cargo later acquired under inner control is never re-captured (the naive
  "hold while carrying" re-capture produced an inner-PICK/wrapper-DROP churn,
  D-2 8 games at the intermediate build — all gone).
- **F-D2 starvation release**: after 3 consecutive Idle choices the worker
  reservation (`banana_idle_unit`) is dropped until a lifecycle-productive
  candidate (ring Chop/Harvest/Plant/Boot) exists; a Bank candidate over
  inner-acquired cargo does NOT re-capture (same churn/takeover reason).
  The resident decision is hoisted BEFORE the delegated inner call so the
  seam fields reflect release on the very turn it begins (banana_action is a
  pure function of the view + wrapper state; hoisting is
  behavior-preserving).
- Post-loss banana stock stays under the I-2/I-15 PICK exclusivity for all
  own units (an inner bank-PICKed banana can only become an unmanaged
  replant: witnessed as new D-5 `outside_ring` + D-6 farming at the
  intermediate build; veto restores the round-5 protection while every other
  economy verb of the released resident is sanctioned).
- F-D3 (chopper-aware flip) remains NOT implemented (not authorized; optional
  in the diagnosis).

### Spec amendment (ruling 3) and R-2a

`invariant-spec-2026-08-04.md` gained the dated block **"Revision 2026-08-06 —
abandonment releases the resident to the inner economy"**: I-10a's "cease all
investment" binds the ASSET (persistent protected-cell claim while the lost
plant lives; no mother-directed verbs) not the worker (held only to bank
leftovers, then released; liveness per I-19/I-20/I-21; banana-stock PICK
exclusivity retained). `regression_tests.py r2_abandon` (R-2a) was amended
exactly that far: the former any-`PLANT` violation clause is now mother-scoped
(`PLANT` on the mother cell); MOVE-toward-mother and on-mother HARVEST/CHOP
clauses unchanged; docstring cites the revision block. **No other test,
detector, or check changed.**

## Ladder

### 1. Build — PASS
`python3 build_banana_candidate.py`: all mechanical asserts green (parent sha
`a8eb3b2b...` verified, anchors unique, per-block compact round-trip,
insertions unique/pairwise non-substring, inverse transform restores the
parent byte-for-byte). I1 insertion 17,763 bytes; total 80,934 < 100,000.

### 2. Compile — PASS
`rustc --edition=2021 -O` (no `-Awarnings`): exit 0, zero warnings, compact
and research sources. Empty stdin: clean exit 0.

### 3. Witness maps (diagnosis consolidated matrix, re-run on the final panel)

| fix | flipped green (turns) | still red (mechanism) |
|---|---|---|
| F-A | m001-s0, m016-s0, m044-s0, m053-s1: D-9 blocking 0, report-tier flags only | m038-s1, m048-s0, m064-s0: byte-identical inherited D-6/D-4 (no gate authorized) |
| F-B | m066-s0 (carrier DROPs t~7, was 26-state alternation to t29), m030-s1, m023-s0 (k=96 gone), m021-s0, m042-s1-P2, m056-s1-P2-window-79-96-shortened | m056-s1/m024-s0/m050-s0 D-1: inner-policy bounces on diverged state, wrapper holds no reservation |
| F-C | m050-s0 (D-6 x15 + D-8 gone), m003-s0, m026-s0, m015-s0 (`opp_chop_eta` gone), m009-s0 (D-6 tail closed) | m060-s1/m035-s1/m036-s1/m025-s1/m066-s1 D-6: foundings at eta 11-13 (above the R-4/t1-bounded margin) lost late |
| F-D | m009-s0/s1 (progress resumes, slot banked), m023-s1, m056-s0 (d1 freezes gone); m012/m028 d2 freezes gone (WAIT-t4-t200 no longer occurs) | m012/m028/m065-s1/m032-s0 P4: opening-forfeit — inner has no work on the diverged state; stall windows are 100% inner WAITs |

### 4. R-1..R-5 + controls — exit 0
`regression_tests.py all --source candidate-banana-r2.min.rs`: R-1, R-2a
(amended predicate, diff documented above), R-2b, R-3a, R-3b, R-4, R-5 all
PASS; compliant controls PASS; `control-r3a-doomed` and `control-r5-oscillator`
FAIL as designed. Old-bytes crosschecks: all five configured red/green pairs
re-verified RED for the documented reason on their old bytes (pre-review
red-reason CLEAR), including `R-5-vs-9f5ef833` (the B-fix subject) and the
R-2a-relevant pairs — the amended R-2a still ERRORs/FAILs old bytes for the
documented mechanisms.

### 5. TIER / detectors / traces — PASS
- TIER-P 7/7, `tier-p-golden.json` **byte-equal to committed** (git clean).
- TIER-C 8/8 (`tier-c-results-v6-2026-08-06.json`).
- `python3 -m unittest test_trace_detectors`: 28/28 OK (file untouched);
  `test_fuzz_panel` 18/18 OK with the D-9 gate; `test_pre_review` OK;
  `conversion_race_oracle.py` self-test OK.
- t1–t6 regeneration (default/`--dynamic`/`--round3`, exits 0/0/0):
  **t2, t3, t4, t5, t6 byte-identical**; **t1 changed** (202/300 command
  lines): same full lifecycle (bootstrap PICK t1, diagonal mother founded,
  harvest/replant service, orth wood cycles, late-cutoff tail) with timing
  shifted a few turns — the F-B3 blocked-counter and F-D2 idle bookkeeping
  change hysteresis tie-breaks on idle-adjacent turns. Justification against
  the spec: `t1_lifecycle-detectors.json` regenerated **byte-identical**
  (D-1..D-9 all PASS, 0 episodes) and `r1-trace` on the new t1 PASSes R-1 —
  **t1 I-9 sequencing holds**. t3/t4 byte-identity means the R-2a/R-2b
  dynamic evidence is unchanged bytes despite the amended semantics (their
  residents are never idle-released post-flip in-window).

### 6. Readable source + behavioral equality — PASS
`rustfmt --edition 2021` regenerated `research-banana-r2.rs`; compiles
standalone, zero warnings. TIER-P fixtures from the research build equal the
committed golden; TIER-C 8/8; closed-loop t1/t2/t3/t4 replays from the
research build **byte-equal** to the committed traces; r1/r2/r3/r4/r5
scenario runs research-vs-compact **byte-equal** (all trace outputs
`diff -r`-equal).

### 7. FULL PRE-REVIEW — **BLOCK, exit 1 (fuzz panel only; ruling-7 stop)**
`python3 pre_review.py --config banana-r2-task-config.json --report
pre-review-r6-2026-08-06.md`: trace-provenance CLEAR, single-model CLEAR,
red-reason CLEAR (5/5 pairs red-for-the-right-reason), claims-coverage CLEAR;
**fuzz-panel BLOCK — 47 of 240 games** (report
`fuzz/fuzz-report-eac2eb36-2026-08-06.md`, failures re-saved under
`fuzz/failures/`). Per ruling 7 the work STOPS here and the residual families
are reported honestly (no threshold/geometry/property tuning beyond ruling 1):

- **violating games 141 → 47** (blocking); by family:
  P4 27, D-1 14, D-4 9, D-6 10, D-7 2, P2 1.
- **7 games are byte-identical to the parent** (`cmp`-proven:
  m038-s0/s1, m048-s0, m075-s0, m095-s1 [D-6]; m064-s0, m106-s1 [D-4]) —
  inherited funding-phase behavior that ruling 1's D-9-only gate cannot
  clear; the D-4/D-6 parent-differential question goes to the integrator.
- The remaining candidate-attributable families are inner-policy behavior on
  candidate-diverged states (stall windows and oscillations occur on turns
  where the wrapper holds no reservation and issues no command — verified on
  sampled games m032-s0, m090-s0, m118-s0, m056-s1, m050-s0) plus the
  opening-forfeit economics of activating at all on chopper-contested maps,
  and 5 late-loss D-6 games whose founding margins are bounded above by the
  committed R-4/t1 witnesses. Fixing these would require touching the inner
  policy blocks, activation-profile gating, or detector tiers — all outside
  this round's authorization.
- D-2, D-5, D-8, D-9 blocking: **0**. P0 crashes: 0. P3 orchard inertness:
  12/12.

### 8. Claims — updated
`banana-r2-claims.json`: the current-bytes citations now name `eac2eb36`
(oracle-boundary claim → this ledger; I-19/I-20/I-21 note the byte-identical
regenerated r5 trace, bank turn 6 unchanged). All evidence paths exist;
claims-coverage CLEAR.

## Notes
- Functional changes: `banana_blocks/block-i1.rs` (regenerated
  `candidate-banana-r2.min.rs`, `candidate-banana-r2-manifest.json`,
  `research-banana-r2.rs`), `claude_1/pipeline/fuzz_panel.py` (+config note),
  `invariant-spec-2026-08-04.md` (dated revision block),
  `regression_tests.py` (R-2a predicate, exactly as amended).
- Trace byte changes: t1 only (justified above); r5 trace regenerated
  byte-identical.
- `fuzz/failures/` now holds the 47+flagged games of the eac2eb36 run; the
  47c98f53 evidence set remains at commit `15e44090` (cited by
  diagnosis-r6-2026-08-06.md).
