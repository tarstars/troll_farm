# RED evidence — R-5 two-worker-full-cargo-banking FAILs on 9f5ef833 (round 5)

Date: 2026-08-05
Candidate under test: `candidate-banana-r2.min.rs`, SHA-256
`9f5ef8336c5268927dd3aef873a1a348dd9e0bb43c2cc1e505b14730352db8a2`
(canonical artifact commit `b358124f`). Parent baseline: `a8eb3b2b...`
(`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`).
Origin: round-4 host review, terminal failure 1 (MULTI_UNIT_COORDINATION):
worker 2 with carry `[0,0,0,0,0,2]` alternates `(8,4)<->(8,3)` for turns
34-258 on map seed 9,854,000 emitting `MOVE 2 8 3` / `MOVE 2 8 4`, no DROP;
margin +68 (parent) -> -93 (candidate). This round is RED-phase only: the
defect class is reproduced locally, mechanized, and proven failing on the
current bytes. NO candidate bytes were changed.

## 1. Reproduction geometry (R-5 scenario, candidate-driven, closed loop)

`make_banana_traces.scenario_r5_two_worker_banking` on `R5_MAP`:

```
##############
#0.###########      tent (1,1); doors (2,1), (1,2)
#............1      east corridor row 2; opponent shack (13,2)
##############
##############
```

Live diagonal banana mother on (2,2) (size 4, fruits 0, cd 60) — the single
articulation cell between the corridor and BOTH doors. Units at turn 1:
resident starter u0 on the (2,1) door (banana phase activates turn 1;
protected cell = (2,2)); second worker u2 at (6,2) with FULL wood cargo
`[0,0,0,0,0,2]`; far opponent harvester u5 at (12,2) (ownership never
flips). Both own workers present from turn 1, mirroring the host's turn-1
training. Deterministic: static opponent, pure function of the command
stream.

## 2. Episode found (real 9f5ef833 binary, 40 turns)

Command stream head (`regression_tests.py r5-bin`):

```
t1  MSG ...;WAIT;MOVE 2 5 2        u2 (6,2) -> (5,2)
t2  WAIT;MOVE 2 4 2                u2 (5,2) -> (4,2)
t3  WAIT;MOVE 2 3 2                u2 (4,2) -> (3,2)
t4  WAIT;MOVE 2 4 2                u2 (3,2) -> (4,2)   <- displacement
t5  WAIT;MOVE 2 3 2
...alternates MOVE 2 3 2 / MOVE 2 4 2 through t40...
```

Episode: unit 2, turns 3-40 inclusive — **38 alternating states
(k = 18 A->B->A cycles), cells (4,2)<->(3,2), carry `[0,0,0,0,0,2]`
unchanged, zero DROP, zero progress events** — same class as the host's
225-turn `(8,4)<->(8,3)` episode (>= 6-turn two-cell alternation with full
wood cargo). It is a stable fixed cycle; it ends only at the trace horizon.

## 3. R-5 verdict on the current bytes: FAIL

`python3 regression_tests.py r5-bin --binary <9f5ef833 binary>` -> exit 1:

```
"check": "R-5 two-worker-full-cargo-banking"
"verdict": "FAIL"
"full_wood_carrier_since": {"2": 1}
"bank_turns": {"2": null}
violations:
 - "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits
    a two-cell alternation cells (4, 2)<->(3, 2) over turns 3-40 (38
    states, >= 3 A->B->A cycles) with cargo unchanged and no DROP -
    violates I-19 ... I-20 ... I-21 ...; a D-1 episode by construction"
 - "full wood carrier since turn 1 never DROPs at a door within the
    bounded banking horizon of 30 turns - I-21 forced banking violated"
```

The check reuses D-1's episode machinery (`trace_detectors.detect_d1`) with
full-cargo carry tracking, plus the bounded banking-horizon clause
(R5_HORIZON = 30 on a 40-turn trace).

## 4. Controls (non-vacuity, both directions)

`python3 regression_tests.py controls` -> exit 0, all 9 as designed:

- `control-r5-compliant` (scripted: carrier transits (2,2) legally, DROPs
  at the (1,2) door at t6, wood credited t7; 32 turns so the horizon clause
  is genuinely evaluated): **PASS** — the check is satisfiable;
- `control-r5-oscillator` (scripted mutant reproducing the host shape:
  approach then alternate (3,2)<->(4,2), never DROP): **FAIL** — the FAIL
  direction is reachable independently of the candidate;
- all seven pre-existing controls unchanged (r1, r2a, r2b, r3a compliant +
  doomed, r3b, r4).

## 5. Parent-vs-candidate first divergence

- Parent CLOSED-LOOP on the identical scenario: banks — `DROP 2` at t10 on
  the (2,1) door, own wood inventory credited (4 by t20 after its own
  chop-cycle wood). No alternation episode.
- Parent OPEN-LOOP on the candidate's own R-5 transcript (identical
  states): first unit-2 divergence at **t4** — state u2=(3,2) full cargo:
  parent `MOVE 2 2 2` (the unique next step toward either door), candidate
  `MOVE 2 4 2` (displaced backward). t1-t3 u0-slot differences are the
  expected resident-reservation divergence (banana active), not the defect.
- Mechanism (full analysis in diagnosis-r5-2026-08-05.md): the C5 third
  protection layer in block-i1.rs lines 830-836 —
  `banana_forbidden = {mother}` fed to
  `MoisanBot::resolve_move_conflicts_with_priority_and_forbidden` — forbids
  the non-priority carrier's one-step landing onto the mother every second
  turn and detours it to the cell it just vacated; the inner policy
  re-plans the same shortest bank route each turn. H1 (I6 retain-filter
  removing the Bank candidate) refuted structurally and by probe; H2 (door
  occupancy) contributing geometry only. Scratch probe neutralizing ONLY
  the forbidden set banks at t6; scratch probe deleting ONLY the I6 filter
  still oscillates.

## 6. t1-t6 byte identity and prior checks

After the additive round-5 changes to make_banana_traces.py and
regression_tests.py, regenerated `t1_lifecycle`/`t2_contested` (default
CLI), `t3_abandon`/`t4_convert` (`--dynamic`), `t5_flip_convert`/
`t6_owned_chop` (`--round3`): **all 12 committed trace files byte-identical**
(sha256 -c OK against the pre-change snapshot; exits 0/0/0).

Prior gates on the current 9f5ef833 bytes, all green and untouched:

| check | result |
|---|---|
| `r1-bin` (R-1 one-seed-reservation) | PASS, exit 0 |
| `r2-bin` (R-2a abandon + R-2b convert) | PASS, exit 0 |
| `r3-bin` (R-3a infeasible-tie + R-3b feasible-edge) | PASS, exit 0 |
| `r4-bin` (R-4 flip-response-reachability) | PASS, exit 0 |
| `controls` (9 = 7 prior + 2 new R-5) | as designed, exit 0 |
| `test_trace_detectors.py` | OK |
| `r5-bin` (NEW) | **FAIL, exit 1 — the round-5 red** |

## 7. Pipeline extension (see claude_1/pipeline/)

- failure-ledger.json: new permanent class `MULTI_UNIT_COORDINATION`
  (origin: the round-4 host review, finding 1; detection mechanized;
  check: the R-5 red/green pair).
- banana-r2-task-config.json: red/green pair `R-5-vs-9f5ef833`
  (old_source_git commit `b358124f`, the current bytes) with the failure
  signature above; critical invariants extended with I-19/I-20/I-21 whose
  claims cite the successor's future green R-5 trace
  (`traces/r5-two-worker-banking-commands.txt`, produced by
  `regression_tests.py r5-bin --outdir traces` only once the defect is
  repaired — deliberately absent now).
- `pre_review.py` on the extended config against the current state:
  **BLOCK** (red-reason: R-5 red for the right reason on the current
  bytes; claims-coverage: I-19/I-20/I-21 green evidence absent by
  construction). Report: `claude_1/pipeline/pre-review-r5-2026-08-05.md`.

A successor is GREEN when: the R-5 carrier reaches a door and DROPs within
the 30-turn horizon with no full-cargo alternation episode, the green trace
is committed at the cited path, all of R-1..R-4 + controls stay green, and
t1-t6 regeneration remains byte-identical for whatever new bytes ship.
