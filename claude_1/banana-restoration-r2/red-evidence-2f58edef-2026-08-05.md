# RED evidence — candidate 2f58edef, round 4 (CONVERSION_RACE_ORACLE unification)

Date: 2026-08-05. Task `20260802-banana-restoration-r2`, round-4 phase 1: unify the
conversion-race oracle across all artifacts, then prove candidate-driven regressions RED on
the current bytes. NO implementation fix is included in this phase.

Candidate under test (unchanged): `candidate-banana-r2.min.rs`, SHA-256
`2f58edef71f692565643cd31c302a32c64543611f920a49f84ff288a663f693b` (verified before and
after this work). Readable pair `research-banana-r2.rs` SHA-256 `2e46b8b1...` (the review's
readable SHA), unchanged. No block, candidate, or build-script changes.

Ground truth: round-3 host review
`data/analysis/live-agent-6553250/banana-restoration-r2-round3-host-review-2026-08-05.md`
and ACK
`coordination/messages/local_codex_1/20260805T143001Z-20260802-banana-restoration-r2-ack.md`
(branch `origin/agent/local_codex_1`).

## 1. The oracle (deliverable 1)

- **Spec**: `invariant-spec-2026-08-04.md`, new block "Revision 2026-08-05 —
  CONVERSION_RACE_ORACLE" defines the single named oracle (inputs, outputs, exact
  absolute-time semantics, strict-tie concession); the I-10a convert clause and the D-8
  exemption clause now cite CONVERSION_RACE_ORACLE by name; the three divergent legacy
  deadlines (spec-old `< eta_opp`, code `< max(eta_opp, predicted.cooldown)`, D-8-old
  `exact_chops < eta_opp_at_chop_start`) are declared void.
- **Reference implementation (once)**: `conversion_race_oracle.py`, function
  `conversion_race_oracle` (deterministic, stdlib only; docstring = the spec text;
  `python3 conversion_race_oracle.py` self-test OK, including an arithmetic cross-check
  against `trace_detectors`' predict/chop mirrors on a state grid).
- **Consumers refactored**: `trace_detectors.detect_d8` (exemption condition (b) is now the
  oracle verdict at the chop-start state) and `regression_tests.py` (R-2b feasibility
  report, new R-3 boundary pair, new R-4) import and use it. The candidate implementation
  is the remaining consumer and is exactly what round 4 phase 2 must fix.

Semantics recap: `completion_turn = t + eta_res + exact_chops - 1` (absolute turn the final
growth-aware chop lands); `opponent_harvest_turn = max(t + eta_opp, first_fruit_turn)`
(HARVEST is executable only standing on the cell with fruits > 0); feasible iff
`completion_turn < opponent_harvest_turn`, strict (equal-turn race conceded).

## 2. R-4 "flip-response-reachability" — FAIL on current bytes (deliverable 2, RED)

Scenario `scenario_r4_flip_reach` (make_banana_traces.py, additive): closed-loop run of the
REAL candidate binary through the deterministic referee — no scripted command stream
anywhere in the check path. The candidate ITSELF:

- turn 1 `PICK 0 BANANA` (bootstrap), turn 2 move, turn 3 `PLANT 0 BANANA` on the diagonal
  mother (2,2);
- turns 4–6 it leaves the mother for its normal lifecycle (orthogonal wood tree at the
  (0,1) door), turns 7–10 `CHOP`, turn 11 `DROP` (bank);
- the opponent harvester (speed 1, from (13,0)) closes in; at turn 11 the resident (at
  (0,1), eta 3) ties the opponent (distance 3): **real I-7 ownership flip, latched**;
- CONVERSION_RACE_ORACLE at the flip turn: eta_res 3, exact chops 5, **completion_turn 18 <
  opponent_harvest_turn 27** (arrival 14, first fruit turn 27) → **feasible, convert
  prescribed**. I-10a window: response must begin at turn 11, or turn 12 at the latest
  (turn 11 is the committed banking DROP, allowed).

Observed on `2f58edef...` (verdict **FAIL**):

```
turn 11: DROP 0          (bank — allowed)
turn 12: WAIT            <- required convert response ABSENT
turns 13..26: WAIT       (terminal abandon loop)
```

The candidate's voided deadline evaluates `eta_res 3 + chops 5 = 8 <
max(eta_opp 2, predicted.cooldown 6) = 6` → false → it takes the abandon branch
(`banana_lost` latch) against an oracle-feasible conversion. This is the reachable,
candidate-driven form of the round-3 review's observed WAIT behaviour: while camping the
flip is unreachable (eta_res 0), and the first reachable flip is answered with WAIT.

Check: `regression_tests.py r4-bin` (`r4_flip_response_reachability`), which also ERRORs
unless the candidate itself planted the mother, a real flip occurred, and the flip-turn
oracle is feasible — scripted evidence cannot pass it. Compact and readable binaries emit
identical command streams on this scenario (verified).

## 3. R-3 boundary pair — geometry at exactly the oracle boundary (deliverable 2)

Fixed geometry (spec Revision 2026-08-05, normative examples;
`scenario_r3a_boundary` / `scenario_r3b_boundary`): near-ripe size-4 mother at (2,2)
(fruits 0, cd 6 → first fruit turn 7), resident on-ring at (2,0) (distance 2, chop 1),
opponent harvester at (4,2) (distance 2, speed 1) camping the mother; I-7 flip at turn 1
(tie 2 vs 2).

- **R-3a (health 5, infeasible by exactly one)**: completion_turn 7 == opponent_harvest_turn
  7 → the strict tie, abandon required; any chop-start is the doomed chop. Current bytes
  **PASS** (abandon). Why they pass despite the arithmetic bug: the voided
  `max(eta_opp, predicted.cooldown)` deadline is *earlier* than the oracle's
  harvest deadline whenever the tree is unripe (a growth cooldown is not ripeness), and the
  voided LHS `eta_res + chops` overstates completion by one — the bug is conservative in
  this direction, so it never accepts an oracle-doomed mother chop. The FAIL direction is
  proven reachable by the scripted `control-r3a-doomed` (chop start turn 3, completion 7 ==
  harvest 7 → R-3a FAIL).
- **R-3b (health 4, feasible by exactly one)**: completion_turn 6 < opponent_harvest_turn 7.
  This is the geometry where the divergent deadline definitions give DIFFERENT answers —
  the discriminating point of the unification (all measured at the turn-1 flip, from the
  candidate trace):

  | definition | comparison | verdict |
  |---|---|---|
  | voided spec-old `< eta_opp` | 6 < 2 | infeasible |
  | voided code `< max(eta_opp, predicted.cooldown)` | 6 < max(2, 4) = 4 | infeasible |
  | voided D-8-old arrival-only (at chop start) | 4 < 0 | infeasible |
  | **CONVERSION_RACE_ORACLE** | completion 6 < harvest 7 | **feasible** |

  Current bytes: **FAIL (RED)** — no CHOP on the mother is ever issued; the candidate
  abandons and WAITs while the referee then shows the opponent harvesting the turn-7 fruit
  the conversion would have denied. `control-r3b-compliant` (convert at the edge: chops
  turns 3–6, tree gone in state 7) PASSes, and the amended D-8 exempts exactly that
  conversion.
- The round-3 unit-level assert STAYS unchanged and green:
  `banana_exact_chop_turns(2, 4, 1, 1) == 5` vs static 4 (plus the same assert against the
  oracle's own mirror).
- Supersession note (documented change 4 in the revision block): the round-3 closed-loop
  scenario `scenario_r3_growth` defined doom by opponent ARRIVAL (turn 6); under the
  unified semantics that conversion was actually feasible (completion 9 < first fruit 23),
  so the old red-on-`280ed777` evidence was for a side reason. The scenario function is
  retained in `make_banana_traces.py` for provenance but no longer drives any verdict.

## 4. Old bytes cross-check (`280ed777`, rebuilt from commit `0ece10ec`)

R-3a PASS, R-3b FAIL, R-4 FAIL — the old bytes refuse the same oracle-feasible conversions
(their static arithmetic differs on chop counts, proven by the retained unit assert, but
their deadline is conservative in the same direction). Both regression REDs therefore
discriminate the unified semantics itself, not an incidental old/new difference.

## 5. Full ledger on current bytes `2f58edef...`

`python3 regression_tests.py all --binary <2f58edef build>` → exit 1 (RED), with:

| check | verdict |
|---|---|
| R-1 one-seed-reservation | PASS |
| R-2a unripe-contested-abandon | PASS |
| R-2b unripe-contested-convert (oracle-based report) | PASS |
| R-3a conversion-race-boundary/infeasible-tie | PASS (see §3) |
| **R-3b conversion-race-boundary/feasible-edge** | **FAIL (RED)** |
| **R-4 flip-response-reachability** | **FAIL (RED)** |
| control-r1 / r2a / r2b / r3a-compliant / r3b-compliant / r4-compliant | PASS (6/6) |
| control-r3a-doomed (FAIL-direction non-vacuity) | FAIL as designed |

Self-tests: `python3 -m unittest test_trace_detectors` → **28/28 OK** (27 prior tests kept
green; the one documented expected-value change re-based
`test_flagged_flip_but_infeasible_chop` on a genuinely oracle-infeasible near-ripe
geometry, since its old scenario's doom was arrival-only and is now correctly exempt — a
new `test_exempt_arrival_is_not_loss` covers that discriminating direction; plus the new
episode fields are asserted). `python3 conversion_race_oracle.py` self-test OK.

## 6. Trace byte-identity (t1–t6)

Regenerated all committed traces with the refactored detectors
(`make_banana_traces.py`, `--dynamic`, `--round3`):

- every `t1..t6` transcript and command file is **byte-identical** (diff over the whole
  `traces/` tree);
- detector JSONs: only `traces/t6_owned_chop-detectors.json` changed — each D-8 episode
  now carries the two oracle fields `completion_turn` / `opponent_harvest_turn`
  (documented change 2); its verdict remains FAIL `discretionary_owned` (t6 is the
  required negative control). t5 remains overall PASS: the oracle re-confirms its
  scripted conversion exempt (completion 16 < harvest 27) — noting per the round-3 review
  that t5 is detector-level evidence only; the candidate-driven case is R-4.

## 7. Determinism / hygiene

All checks are pure functions of (transcript, commands); referees and scripts are
deterministic; stdlib only; no candidate, block, or build-script bytes were touched;
compact and readable binaries produce identical command streams on r3a/r3b/r4.
