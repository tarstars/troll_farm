# Gate results v3 — banana-restoration-r2 round-3 GREEN (exact growth-aware conversion)

Date: 2026-08-05
Task: `20260802-banana-restoration-r2`, round 3 GREEN phase.
Toolchain: rustc 1.97.1, `--edition=2021 -O` (NO `-Awarnings`), Python 3 stdlib
only, fully deterministic.

## Candidate

- NEW: `candidate-banana-r2.min.rs`, **76,750 bytes**, sha256
  `2f58edef71f692565643cd31c302a32c64543611f920a49f84ff288a663f693b`
- OLD (rejected, round-3 RED): 76,386 bytes, sha256
  `280ed777134a7f40783d759d0d327c1e70dece80680fc246675bc0a3c9eae9e6`

## The fix (block-i1.rs only; wrapper conversion branch, I-10a)

The static conversion feasibility `ceil(current_health / chop_power)` against
the decision-turn cooldown-as-ripen proxy is replaced by the exact
growth-aware race, REUSING the source's own mechanics (no second growth
model):

1. predicted plant state at chop start = `MoisanBot::predict_tree` over the
   resident's travel eta (growth during travel included);
2. exact chop duration from that state = `MoisanBot::chop_outcome` (growth
   during the chop sequence included — the review boundary size 2 / health 4
   / cooldown 1 / chop 1 now costs 5 chops, not the static 4);
3. the race must still be OPEN: an opponent harvester already standing on
   the mother (`eta_opp == 0`) has arrival_turn <= decision turn, so no
   conversion can complete strictly before its arrival — infeasible;
4. strict race: `eta_res + exact_chops < max(eta_opp, ripen_at_chop_start)`
   (ties lose, per I-10a "strictly before"); ripen uses the PREDICTED
   cooldown at chop start for an unripe mother, 0 for a ripe one;
5. infeasible => the existing Abandoned transition (I-10a branch 3);
6. committed-conversion latch: the I-10a response is decided ONCE, at the
   first ownership-flip turn ("the resident responds deterministically at
   the first such t"); a committed conversion (`banana_target ==
   (Chop, mother)`, set nowhere else — ring Chop candidates are
   orthogonal-only) runs to completion without re-arbitration, so the race
   won at commitment is not spuriously re-opened when the opponent arrives
   mid-sequence; the mother's death invalidates the latch.

This preserves the amended-D-8 semantics: conversion only after an actual
I-7 flip plus a strict exact-race win; while owned, no discretionary
diagonal-mother chop is ever emitted (unchanged code path).

On the review counterexample the new arithmetic rejects (`0 + 5 exact chops
!< max(5, 1) = 5`) exactly where the static arithmetic accepted (`4 < 5`).

## Ladder

### 1. Build — PASS

`python3 build_banana_candidate.py`: all mechanical asserts green (anchors
unique, per-block compact round-trip, insertions unique/pairwise
non-substring, inverse transform restores the parent sha
`a8eb3b2b...` byte-for-byte). I1 insertion 13,579 bytes; total 76,750.

### 2. Compile — PASS

`rustc --edition=2021 -O` (no `-Awarnings`): exit 0, **zero warnings**
(empty stderr). Empty stdin: clean exit 0, no output, no panic.

### 3. R-3 before/after pair (the round-3 red/green flip)

| bytes | R-3 growth-aware-conversion | exit |
|---|---|---|
| OLD `280ed777...` | **FAIL** — doomed chops turns 6-9, "exact growth-aware completion turn 9 is not strictly before opponent arrival turn 6 (static arithmetic accepted 4 < 5)" | 1 |
| NEW `2f58edef...` | **PASS** — flip turn 1 (eta 5 vs 5), `chop_analysis: null` (no chop on the mother ever) | 0 |

New-candidate r3 behavior: the resident reaches the mother at turn 6 under
the inner policy, the wrapper activates and the exact-race check rejects
(opponent already on the mother, race closed) -> Abandoned latch, WAIT from
turn 6 on. Falsifiability retained: `control-r3-compliant` PASSes.

### 4. Full regression suite on NEW bytes — 8/8 PASS (exit 0)

R-1 one-seed-reservation, R-2a unripe-contested-abandon, R-2b
unripe-contested-convert, R-3 growth-aware-conversion, control-r1,
control-r2a, control-r2b, control-r3: **all PASS**. (t4's convert decision
at its flip turn is `1 + 1 < max(1, 26)` under the exact arithmetic —
convert, latched through the opponent's arrival; t2/t3 abandon decisions
unchanged.)

### 5. TIER-P / TIER-C — PASS

- TIER-P 7/7 PASS, byte-equal vs the committed `tier-p-golden.json`
  (harness re-run drifts only the parent-path metadata inside the file;
  the committed golden is untouched in git, `git diff` clean).
- TIER-C 8/8 PASS (`tier-c-results-v3-2026-08-05.json`).

### 6. Detectors D-1..D-9 (amended D-8) on regenerated t1-t6 — PASS as required

`make_banana_traces.py`, `--dynamic`, `--round3` re-run with the NEW
candidate: **all 18 committed trace files byte-identical** (`sha256sum -c`
all OK, `git diff traces/` empty) — t1/t2 mandatory identity holds, and
t3/t4 (candidate-driven) are ALSO byte-identical because the exact
arithmetic reaches the same abandon/convert decisions at the same turns in
those scenarios; t5/t6 are scripted. Verdicts:

- t1-t4: overall PASS, all nine detectors green.
- t5_flip_convert: overall PASS — the own-plant -> flip -> feasible
  conversion (exact chops 5 < opp ETA 7 at chop start) remains **exempt and
  feasible** under amended D-8.
- t6_owned_chop: D-8 FAIL with 3 `discretionary_owned` episodes, all other
  detectors PASS — the required negative control, unchanged.

### 7. Readable research source — PASS

`rustfmt --edition 2021 --emit stdout < candidate-banana-r2.min.rs >
research-banana-r2.rs`: 3,397 lines, 151,252 bytes, sha256
`2e46b8b1e539878bd291031a75c09edfcb7ad04baf44f8d9985d7cd51375ea3d`.
Compiles standalone with zero warnings. Behavioral equality vs compact:

- TIER-P 7/7 byte-equal to the same golden; TIER-C 8/8 PASS on the research
  source;
- closed-loop referee re-runs t1 (300), t2 (60), t3 (20), t4 (20):
  transcript+commands **byte-equal** to the committed traces;
- r3 growth scenario: research-vs-compact paired run byte-equal, R-3 PASS
  on the research-driven trace.

### 8. Detector self-tests — 27/27 OK

`python3 test_trace_detectors.py`: Ran 27 tests, OK (unmodified).

## Notes

- No test, regression check, detector, or fixture was modified; the only
  functional change is `banana_blocks/block-i1.rs` (conversion branch +
  latch + comments), plus the regenerated candidate/manifest/research
  artifacts and this ledger.
- Trace byte changes: **none** (t1-t6 all byte-identical to committed).
