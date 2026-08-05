# Gate results v4 — banana-restoration-r2 round-4 GREEN (CONVERSION_RACE_ORACLE in code)

Date: 2026-08-05
Task: `20260802-banana-restoration-r2`, round-4 phase 2 (GREEN): make the candidate
implement CONVERSION_RACE_ORACLE and make the I-10a flip response reachable from every
active state. RED evidence for this phase: `red-evidence-2f58edef-2026-08-05.md`.
Toolchain: rustc 1.97.1, `--edition=2021 -O` (NO `-Awarnings`), Python 3 stdlib only,
fully deterministic.

## Candidate

- NEW: `candidate-banana-r2.min.rs`, **77,397 bytes**, sha256
  `9f5ef8336c5268927dd3aef873a1a348dd9e0bb43c2cc1e505b14730352db8a2`
- OLD (round-4 RED): 76,750 bytes, sha256
  `2f58edef71f692565643cd31c302a32c64543611f920a49f84ff288a663f693b`

## The fix (block-i1.rs only; the two defects named by the red evidence)

**(a) REACHABILITY.** The I-10a ownership check was gated on `carry[WOOD] == 0`, so a
flip landing during the wood cycle was structurally unanswerable from that state (R-4's
observed DROP-then-WAIT window). Now ownership (I-7, resident ETA vs minimal
opponent-harvester ETA, ties conceded) is re-evaluated on EVERY active turn — wood-cycle,
camping and banking included — and the response (harvest-now / convert / abandon)
preempts whatever the resident was doing. The single sanctioned deferral (I-10a rev.
2026-08-05, I-19) is an already-committed banking DROP executing at the flip turn itself:
standing on a door with wood, the DROP banks the cargo and the response begins wood-free
at `t + 1` (`banking_drop_now` guard). The committed-conversion latch also moved outside
the wood gate, so a preempting conversion is never interrupted by leftover cargo.

**(b) DEADLINE.** The voided `eta_res + chops < max(eta_opp, predicted.cooldown)`
comparison (and its arrival-only `eta_opp > 0` "race still open" guard) is replaced by
the oracle semantics, mirroring `conversion_race_oracle.py` exactly in the shared
absolute frame anchored at the decision turn t:

- arrival state = growth-only forward simulation over `eta_res` — new helper
  `banana_predict_growth`, the oracle's `predict_tree` mirror. Deliberately NOT
  `MoisanBot::predict_tree`: the inner policy's predictor folds in the
  `predicted_opp_chop` attrition heuristic, which the oracle forbids (on the r3a
  geometry that heuristic would under-count health and start the doomed chop);
- `exact_chops` = `MoisanBot::chop_outcome` from the arrival state (unchanged reuse);
- `completion_turn = t + eta_res + exact_chops - 1`;
- `opponent_harvest_turn = max(t + eta_opp_h, first_fruit_turn)` with the ripeness wait
  taken from `MoisanBot::ticks_until_fruit` — the oracle's `first_fruit_delay` mirror
  for live bananas (0 if ripe now; natural-growth ticks to the first fruit otherwise);
- feasible iff `completion_turn < opponent_harvest_turn`, STRICT. Both sides share the
  anchor t, so the emitted comparison `eta_res + chops - 1 < max(eta_opp, ripe)` IS the
  oracle's absolute one.

No test, regression check, detector, oracle, or fixture was modified.

## Ladder

### 1. Build — PASS

`python3 build_banana_candidate.py`: all mechanical asserts green (parent sha
`a8eb3b2b...` verified, anchors unique, per-block compact round-trip, insertions
unique/pairwise non-substring, inverse transform restores the parent byte-for-byte).
I1 insertion 14,226 bytes; total 77,397 (< 100,000 budget).

### 2. Compile — PASS

`rustc --edition=2021 -O` (no `-Awarnings`): exit 0, **zero warnings** (empty stderr),
both compact and research sources. Empty stdin: clean exit 0 on both binaries.

### 3. R-4 / R-3b before-after pair (the round-4 red/green flip)

| bytes | R-4 flip-response-reachability | R-3b feasible-edge | R-3a infeasible-tie |
|---|---|---|---|
| OLD `2f58edef...` | **FAIL** (DROP t11, then WAIT t12–26) | **FAIL** (no mother CHOP ever) | PASS |
| NEW `9f5ef833...` | **PASS** | **PASS** (chops turns 3–6) | PASS |

R-4 on the new bytes — the flip response is now observable in the candidate-driven
trace (flip turn 11, tie 3 vs 3; oracle: completion 18 < opponent harvest 27, feasible):

```
turn 11: DROP 0        (the committed banking DROP — sanctioned deferral)
turn 12: MOVE 0 0 2    <- convert response begins at f + 1 (window [11, 12])
turn 13: MOVE 0 1 2
turn 14: MOVE 0 2 2
turns 15-19: CHOP 0    (5 growth-aware chops; final chop lands turn 19 < 27)
turn 20: MOVE 0 2 1
turn 21: DROP 0        (conversion wood banked)
```

`response_begun_turns = [12]`, `chop_turns_on_mother = [15..19]` — the R-4 checker's
scenario-validity gates (candidate-planted mother at t3, real flip, feasible flip-turn
oracle) all hold. R-3b: flip turn 1, oracle completion 6 < harvest 7 (the geometry where
every voided legacy deadline says infeasible) → convert accepted, chops turns 3–6.
R-3a: the strict tie (7 == 7) still abandons, `chop_analysis: null` — the boundary is
respected in both directions on the same geometry.

### 4. Full regression suite on NEW bytes — exit 0

`regression_tests.py all --binary <9f5ef833 build>`: R-1, R-2a, R-2b, R-3a, R-3b, R-4
all PASS; controls r1/r2a/r2b/r3a/r3b/r4 compliant all PASS; `control-r3a-doomed` FAILs
as designed (FAIL-direction non-vacuity retained). R-1/R-2a/R-2b verdicts unchanged
from the red ledger.

### 5. TIER-P / TIER-C — PASS

- TIER-P 7/7 PASS, fixtures **byte-equal** to the committed `tier-p-golden.json`
  (re-run golden differs only in the parent-path metadata outside `fixtures`; the
  committed golden is untouched in git).
- TIER-C 8/8 PASS (`tier-c-results-v4-2026-08-05.json`).

### 6. Detectors D-1..D-9 on regenerated t1–t6 — PASS as required, zero byte drift

`make_banana_traces.py`, `--dynamic`, `--round3` re-run with the NEW candidate:
**all committed trace files byte-identical** (`git status traces/` clean) — no
turn-level diffs to document:

- t1/t2: identical as mandated. Analysis of why the reachability change cannot move t1:
  the static opponent sits 13+ cells out, so `eta_res >= eta_opp_h` never holds and the
  new every-turn check falls through to the identical candidate flow on every turn
  (I-9 sequencing untouched — same commands, same bank/plant order). t2's turn-1 flip
  is wood-free and oracle-infeasible (completion 9 ≥ harvest 3), same abandon as before.
- t3/t4 (candidate-driven): the oracle reaches the same abandon/convert decisions at
  the same turns as the voided deadline (t3 flip is deep-infeasible either way; t4's
  cd-30 mother makes both deadlines accept), so the commands are byte-identical.
- t5 PASS (scripted, D-8 exemption re-confirmed by the oracle), t6 D-8 FAIL
  `discretionary_owned` — the required negative control, unchanged.

### 7. Readable research source — PASS

`rustfmt --edition 2021 --emit stdout < candidate-banana-r2.min.rs >
research-banana-r2.rs`: 3,425 lines, 152,233 bytes, sha256
`f2406fe7a6a454c640592b9867f5a12784cc7c2d63f0d31de664e5d1defae9c2`. Compiles standalone
with zero warnings. Behavioral equality:

- TIER-P 7/7 fixtures byte-equal to the same committed golden; TIER-C 8/8 PASS on the
  research source;
- closed-loop referee re-runs t1 (300), t2 (60), t3 (20), t4 (20):
  transcript+commands **byte-equal** to the committed traces;
- r3a/r3b/r4 scenarios: research-vs-compact paired runs **byte-equal** (hence identical
  R-3/R-4 verdicts on the research-driven traces).

### 8. Self-tests — OK

`python3 -m unittest test_trace_detectors`: **28/28 OK** (unmodified).
`python3 conversion_race_oracle.py`: self-test OK (includes the retained round-3 unit
assert `banana_exact_chop_turns(2, 4, 1, 1) == 5` and the trace_detectors cross-check).

## Notes

- Only `banana_blocks/block-i1.rs` changed functionally; regenerated artifacts:
  `candidate-banana-r2.min.rs`, `candidate-banana-r2-manifest.json`,
  `research-banana-r2.rs`, plus `tier-c-results-v4-2026-08-05.json` and this ledger.
- Trace byte changes: **none** (t1–t6 all byte-identical to committed).
