# RED evidence — regression checks vs rejected candidate f29efd0e

Task: test-driven retry, RED phase, for `20260802-banana-restoration-r2`.

Candidate under test: `candidate-banana-r2.min.rs`, SHA-256
`f29efd0e9c8cd17a2151678b2b0a449baba76aa12ede283d5ef486f5a5fe6eb9`
(verified with `sha256sum` immediately before compiling; this is the exact
byte set the host review rejected). No fix was implemented; the candidate,
harness fixtures, detectors, spec, and committed traces are untouched.

Compile of the rejected bytes (from `claude_1/banana-restoration-r2/`,
`$SP` = the session scratchpad `.../scratchpad/banana`):

```
rustc --edition=2021 -O --crate-name reject_check \
      -o "$SP/reject_check" candidate-banana-r2.min.rs
```

New instruments (this phase, additive only):

- `make_banana_traces.py` — added `DynamicOpponentReferee` (opponent
  harvester MOVEs toward a target mother at its own speed via the same
  `step_toward` mirror and harvests one ripe fruit per turn on arrival),
  scenario factories `scenario_t3_abandon` / `scenario_t4_convert`, and a
  `--dynamic` CLI flag. The default (no-argument) path is untouched.
- `regression_tests.py` — checks R-1 "one-seed-reservation" (I-9) and
  R-2 "unripe-contested-response" (I-10a), as trace analyses with a CLI
  usable against any candidate binary or trace file. Spec language is
  quoted in the docstrings.

## Existing t1/t2 fixtures regenerate byte-identically

```
python3 make_banana_traces.py         # default path, rejected candidate
cmp traces/<f> $SP/traces-baseline/<f>   # baseline = pre-change copies
```

Result: `t1_lifecycle PASS ... t2_contested PASS ...` and `cmp` reports all
six files identical (`t{1,2}*-transcript.txt`, `*-commands.txt`,
`*-detectors.json`), both after the code change and again after producing
the new `t3_abandon` / `t4_convert` traces with `--dynamic`. The dynamic
extension changed nothing in the existing scenario outputs.

## R-1 "one-seed-reservation" (I-9) — FAIL on the rejected bytes

I-9: "Replant demand ... has priority for at most one carried seed; every
additional carried banana is surplus and must be on a bank path (... then
DROP)." R-1 fails a trace when the resident issues `PLANT <id> BANANA`
inside an open unbanked-surplus window (open from the first turn with
banana carry > 1 until a DROP at a door, or until the carried bananas are
gone).

Trace-file mode against the EXISTING committed trace (deliverable 4):

```
python3 regression_tests.py r1-trace \
    --transcript traces/t1_lifecycle-transcript.txt \
    --commands  traces/t1_lifecycle-commands.txt
```

Verdict: **FAIL**, 18 violations, exit 1. The first two are exactly the
host review's t55–t61 pattern (`HARVEST 0` at t55 and t56, carry 2 at t57):

| turn | carry before command | command | surplus since |
|---:|---:|---|---:|
| 58 | 2 | `PLANT 0 BANANA` | 57 |
| 61 | 1 | `PLANT 0 BANANA` | 57 |

First subsequent bank: `DROP` at t79 — after both plants, matching the
review table. The same two-plants-before-banking pattern repeats each
cycle (violations at t68/71, t113/116, t123/126, t168/171, t178/181,
t223/226, t233/236, t278/281).

Closed-loop mode against the compiled rejected bytes reproduces the same
result (deterministic re-run of the t1 lifecycle scenario, 300 turns):

```
python3 regression_tests.py r1-bin --binary "$SP/reject_check" \
    --outdir "$SP/red-run"
```

Verdict: **FAIL** with the identical violation list, exit 1.

## R-2 "unripe-contested-response" (I-10a) — FAIL on the rejected bytes

I-10a: on ownership loss (I-7 flips false, ties not owned) the resident
must harvest now if a ripe fruit is immediately harvestable, otherwise
convert iff the chop completes strictly before `eta_opp`, else abandon
("no further commands invested in the asset").

```
python3 regression_tests.py r2-bin --binary "$SP/reject_check" \
    --outdir "$SP/red-run"
```

### Variant A — `t3_abandon` (conversion impossible ⇒ Abandoned required)

Unripe mother (2,2) size 4 health 6 cd 6; resident (speed 1, chop 1) at
(5,3), owned at turn 1 (eta 4 < 5); opponent harvester (speed 2) closes
from (11,2). Ownership flips at **turn 6** (tie, eta_res = eta_opp = 0,
`unripe_at_flip: true`); conversion (travel + 6 chop turns) cannot
complete strictly before the opponent's earliest harvest. Verdict:
**FAIL** — the rejected candidate keeps investing in the lost asset:

| turn | command | violation |
|---:|---|---|
| 7 | `HARVEST 0` | HARVEST on the lost mother (opponent-owned fruit) |
| 9 | `PLANT 0 BANANA` | PLANT after ownership flip |
| 13 | `MOVE 0 2 2` | MOVE toward the lost mother |
| 19 | `MOVE 0 2 2` | MOVE toward the lost mother |

No `Abandoned` behavior exists: the unripe contested mother fell through
to normal investment, exactly as the host review found. The dynamic
opponent then captures fruit from that mother (its banana carry reaches 2
in the `--dynamic` t3 trace) — the capture path the static-opponent
mini-referee could never exercise.

### Variant B — `t4_convert` (conversion possible ⇒ CHOP required)

Unripe pre-damaged mother (2,2) size 4 health 2 cd 30; resident at the
(2,1) door (chop 1: conversion completes by turn 3); opponent harvester
(speed 2) camps on the mother. At the first not-owned turn the analyzer
reports `chop_completes_by: 3` vs `opp_earliest_harvest: 27` —
`conversion_possible: true`. Verdict: **FAIL** — the rejected candidate
emits `WAIT;WAIT` for all 20 turns; `chop_turns_on_mother: []`, no CHOP
ever begins. No convert-vs-abandon decision exists for an unripe
contested mother.

## Near-miss controls — both checks CAN pass (not vacuous)

```
python3 regression_tests.py controls        # exit 0
```

- `control-r1-compliant`: scripted resident harvests two (carry 2, window
  opens), banks via `DROP` at the (2,1) door at t4, then replants a later
  single seed with carry exactly 1 → R-1 **PASS**.
- `control-r2a-compliant`: same `t3_abandon` dynamic scenario, scripted
  resident retreats to (1,2) and idles (flip at t5, unripe) → R-2a
  **PASS**.
- `control-r2b-compliant`: same `t4_convert` dynamic scenario, scripted
  resident chops the mother at t2/t3, strictly before the opponent's
  earliest harvest → R-2b **PASS**.

## Summary

| check | rejected bytes f29efd0e | compliant control |
|---|---|---|
| R-1 one-seed-reservation (I-9) | FAIL (t58 carry 2, t61 carry 1, ... ; bank only at t79) | PASS |
| R-2a unripe-contested-abandon (I-10a) | FAIL (HARVEST t7, PLANT t9, MOVE t13/t19 after flip t6) | PASS |
| R-2b unripe-contested-convert (I-10a) | FAIL (no CHOP; 20×WAIT despite chop-by-3 vs eta 27) | PASS |

Both host-review findings are now pinned by regression tests that fail on
the rejected implementation and pass on compliant behavior. RED phase
complete; no fix was implemented.
