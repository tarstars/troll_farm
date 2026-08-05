# Gate results v2 — candidate-banana-r2 GREEN retry (2026-08-05)

Candidate: `claude_1/banana-restoration-r2/candidate-banana-r2.min.rs`,
76,386 bytes, sha256 `280ed777134a7f40783d759d0d327c1e70dece80680fc246675bc0a3c9eae9e6`
(**new hash**; replaces rejected `f29efd0e9c8cd17a2151678b2b0a449baba76aa12ede283d5ef486f5a5fe6eb9`).
Parent: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`,
62,725 bytes, sha256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` (verified by the build).

Scope of the change: **implementation only** — readable block `banana_blocks/block-i1.rs`
(the I1 insertion internals). No test, detector, fixture assertion, regression check,
harness, spec, or seam-structure change. Blocks I2–I6, all anchors, and the insert-only /
inverse-transform properties are untouched. No fixture data change was needed (the
spec-cited-update allowance was not used; see gate 5/6 notes).

## Implementation delta (fixes the two host-review terminal failures)

1. **I-9 one-seed reservation (host finding 1 / R-1).** `banana_candidates` now derives
   `surplus = carry[BANANA] > 1`: while the plot has replant demand at most ONE carried
   banana is reserved as the seed; while any surplus is carried, **no Plant candidate is
   offered at all** and the banking candidates are offered instead
   (`total_carried > 0 && (!carried || !demand || surplus)`), so every banana beyond the
   reserved seed is on a door bank path (then `DROP`) **before** any further planting.
   Since carried bananas only ever decrease via `PLANT` (now blocked while surplus) or a
   door `DROP` (which banks the whole cargo and closes the surplus window), the R-1 window
   predicate can never observe a PLANT inside an open unbanked-surplus window.
2. **Full I-10a ownership-loss response (host finding 2 / R-2a, R-2b).** The old
   `contested && fruits_ready` special case is replaced by the complete deterministic
   decision, re-evaluated as a pure function of `S_t` on every wood-free turn: the mother
   is LOST at the first turn with `eta_res >= eta_opp_h` (I-7 committed-harvester ETA,
   ties conceded); then
   - ripe fruit harvestable **immediately** (resident standing on the mother, fruit ready,
     capacity free) → `HARVEST` now;
   - else **convert** iff `eta_res + ceil(health/chop_power) < max(eta_opp_h, ripen)`
     (the opponent's earliest possible harvest; an unripe mother is bounded below by its
     ripening cooldown) → `CHOP` the mother at current size (deliberate, see D-8 note);
   - else the **Abandoned transition**: `banana_phase = Abandoned`, new `banana_lost`
     flag set, target and mother protection (`banana_protected_cell`) released, and the
     resident thereafter emits only bank-leftovers/`WAIT` (`banana_lost_action`) — no
     PLANT, no mother-directed verb. The resident **stays reserved**
     (`banana_idle_unit`) in this state: releasing it would let the inner policy reinvest
     in the opponent-owned asset (exactly the pre-fix t3 failure mode where the inner
     policy chased the lost mother's fruit).
   The farther-away-ripe-fruit case the host review cited (t2: fruit ready, resident ETA 3
   vs opponent ETA 2) now falls through harvest-immediately (not immediate) and convert
   (9 ≥ 2) to Abandoned — no MOVE toward opponent-owned ready fruit is possible.

## Gate ladder

### 1. Build asserts (`build_banana_candidate.py`) — ALL PASS

Six insertions at the identical anchors; all mechanical asserts green: parent sha
verified; per block `compact(readable) == inserted` (I2/I3/I4/I6 additionally equal the
seam-fixed exact bytes — unchanged); every anchor count == 1 in parent; every inserted
string count 0 in parent / 1 in output; pairwise non-substring; **inverse transform:
sha256(output minus the six insertions) == parent sha** — reproduced on this build.
I1 inserted bytes grew 11,554 → **13,215** (the only changed insertion). Candidate
76,386 bytes < 100,000 (budget PASS). Manifest regenerated:
`candidate-banana-r2-manifest.json` (records the new candidate sha `280ed777...`).

### 2. Compile — PASS

`rustc --edition=2021 -O` **without** `-Awarnings`: exit 0, zero warnings (stderr empty).
Empty stdin: exit 0, zero stdout, zero stderr.

### 3. Regression checks R-1 / R-2a / R-2b (the GREEN point) — ALL PASS, controls PASS

`python3 regression_tests.py all --binary <green build>` → exit 0 (tests byte-unchanged
from the committed RED phase):

| check | rejected f29efd0e (re-run 2026-08-05) | new candidate 280ed777 |
|---|---|---|
| R-1 one-seed-reservation (I-9) | **FAIL** (exit 1, same violation list) | **PASS** (0 violations) |
| R-2a unripe-contested-abandon (I-10a) | **FAIL** (exit 1) | **PASS** (flip t6, 0 violations) |
| R-2b unripe-contested-convert (I-10a) | **FAIL** (exit 1, no CHOP) | **PASS** (flip t4, `chop_completes_by 3 < opp_earliest 27`, chops t5/t6) |
| controls (r1/r2a/r2b compliant) | PASS | PASS (unchanged — not vacuous) |

Continuity: the rejected bytes were re-verified (`sha256sum` = `f29efd0e...`) and re-run
through the identical unchanged checks immediately before this build — still FAIL —
giving the before/after pair above. R-1 additionally PASSES in trace-file mode against
the regenerated committed `traces/t1_lifecycle-*` (the RED deliverable-4 mode).

### 4. TIER-P parent-dormancy — 7/7 BYTE-EQUAL

New candidate diffed line-for-line + stdout-sha against the **committed**
`tier-p-golden.json` (byte-identical in git; the harness re-run drifted only the
parent-path metadata string, reverted as in v1 note 8.7): p_baseline_plain,
p_orchard_eligible, p_banana_inventory_dormant, p_wood_banking, p_two_worker,
p_late_window, p_training — all byte-equal. Inertness survives the fix (both new code
paths are reachable only in banana-Active/lost states).

### 5. TIER-C — 8/8 PASS (`tier-c-results-2026-08-05.json`)

All eight fixtures PASS **with unmodified fixture assertions** — no fixture encoded the
buggy behavior, so no spec-cited fixture update was needed. One recorded behavioral
detail change inside a passing fixture: in `c_banking`, the door-standing carrier with
TWO bananas now resolves by `DROP` (bank the surplus first, I-9) where the rejected
candidate resolved by `PLANT`; the fixture accepts either verb by design
("DROP (bank) or PLANT (the one replant-priority seed of I-9)"), which is exactly the
I-9 distinction this retry implements.

### 6. Detectors D-1..D-9 on regenerated closed-loop traces — ALL PASS (4 × 9)

`make_banana_traces.py` (t1/t2) and `--dynamic` (t3/t4) regenerated against the new
candidate; library reports `traces/*-detectors.json` and byte-identical CLI runs
`*-detectors-cli.json`. All 36 detector verdicts PASS. Detector self-tests: 23/23 OK
(detectors untouched).

- **t1_lifecycle changed bytes — expected (the fix).** New pattern per cycle:
  HARVEST ×2 → MOVE to door → `DROP` (bank surplus) → return → HARVEST 1 → PLANT with
  carry exactly 1 (e.g. t55-58 bank, t65-67 single-seed plant). 15 plants, 29 door
  DROPs, bootstrap PICK still 1, ownership never flips (far static opponent).
- **t2_contested changed bytes — expected.** The mother is lost at turn 1 (resident ETA 3
  ≥ opponent ETA 2, fruit ripe but not immediate, convert 9 ≥ 2) → Abandoned: the
  resident no longer chases opponent-owned ready fruit (the exact fault the host review
  named); trace is the MSG banner + reserved-idle WAITs, detectors all PASS.
- **t3_abandon:** dormant-phase prefix identical (inner policy walks the starter to the
  ring, activation t5), flip t6 → Abandoned; WAIT from t5 on; zero post-flip investment.
- **t4_convert:** owned WAITs t1-3, flip t4 → convert (MOVE t4, CHOP t5/t6), wood banked
  (MOVE t7, DROP t8), feature completes and releases; inner emits WAIT thereafter.

**D-8 / I-10a convert resolution note (recorded per orchestrator instruction):** the
spec tension is resolved the way the integrator's review implies — the convert branch
**chops the flipped mother deliberately** as the specified ownership-loss response, and
D-8's diagonal-mother protection is scoped to **non-flipped** mothers. The D-8 detector
was **not modified**. As implemented, D-8 keys on own-`PLANT`ed diagonal bananas
(`own_banana_history`); in the t4 trace the converted mother is scenario-preexisting
(never our PLANT event), so D-8 records 0 episodes and no detector conflict materializes
on any committed trace — the t4 trace demonstrates the chop as the specified response
(R-2b PASS) with D-8 PASS on the same trace. Residual conflict left for integrator
adjudication: a future trace in which an **own-planted** diagonal mother flips and is
converted would be flagged by D-8 as written (its predicate carries no flipped-mother
exemption), while I-10a as revised requires that chop; the detector text/threshold
("0, at any turn including endgame") and the I-10a convert branch cannot both be
satisfied on such a trace. Not triggerable in the current fixture/trace set; flagged, not
patched.

### 7. Missing-artifact fix: complete compilable readable research source — PASS

`research-banana-r2.rs` (3,378 lines, 150,137 bytes, sha256
`9803fea948bcc9a7b28769f997a70c5ff141565304ba5abdaa977d86210cdf61`), derived
mechanically from the built candidate, mirroring the family's readable pipeline
(seam report C.3):

```
rustfmt --edition 2021 --emit stdout < candidate-banana-r2.min.rs > research-banana-r2.rs
```

- Compiles standalone: `rustc --edition=2021 -O` (no `-Awarnings`) → exit 0, zero
  warnings.
- **Behavioral equality vs the compact candidate** (identical command streams):
  - all 7 TIER-P payloads: byte-equal stdout;
  - all 8 TIER-C fixtures re-executed with every internal harness run paired
    compact-vs-research (66 paired payload runs total): byte-equal stdout on every run;
  - all four referee traces t1 (300), t2 (60), t3 (20), t4 (20) re-run closed-loop with
    the research binary: transcript+commands byte-equal to the compact candidate's runs
    **and** to the committed `traces/` files.

## Residual items

- The v1 note 8.2 ("convert unreachable, I-10a-vs-I-14 tension") is superseded by the
  D-8/convert resolution note in gate 6 above.
- Replay-gate items unchanged and still with `local_codex_1` (seam R8): broad
  dormant-equality panel, banana-live replays, host-only gate on game `897829265`, and
  the `897829265` + value-panel resumption the host review conditions on this revision.
