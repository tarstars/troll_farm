# pre_review report - 20260802-banana-restoration-r2

- config: `banana-r2-task-config.json`
- checks run: trace-provenance, single-model, red-reason, claims-coverage, fuzz-panel

## Per-check verdicts

| check | verdict | findings |
|---|---|---|
| trace-provenance | CLEAR | 0 |
| single-model | CLEAR | 0 |
| red-reason | CLEAR | 0 |
| claims-coverage | CLEAR | 0 |
| fuzz-panel | BLOCK | 1 |

## Ledger class coverage

| class | mechanism | status this run |
|---|---|---|
| VACUOUS_EVIDENCE | claims-coverage | clear this run |
| SCRIPTED_TRACE | trace-provenance | clear this run |
| MODEL_DIVERGENCE | single-model | clear this run |
| RED_WRONG_REASON | red-reason | clear this run |
| MULTI_UNIT_COORDINATION | red-reason | clear this run |
| INSTRUMENT_GAP | checklist | n/a (adversarial pre-review) |
| SPEC_TEST_GAP | claims-coverage | clear this run |
| UNSAMPLED_STATE_SPACE | fuzz-panel | BLOCK (1 finding(s)) |
| MISSING_DELIVERABLE | claims-coverage | clear this run |

## trace-provenance - CLEAR

### Notes

- t1_lifecycle: regeneration MATCH (300 command lines byte-identical)
- t2_contested: regeneration MATCH (60 command lines byte-identical)
- t3_abandon: regeneration MATCH (20 command lines byte-identical)
- t4_convert: regeneration MATCH (20 command lines byte-identical)
- t5_flip_convert: declared scripted control (allowed, non-critical). round-3 scripted D-8-amendment illustration, retained for provenance only; the candidate-driven flip/convert evidence is R-4 flip-response-reachability (regression_tests.py r4-bin), which runs the real binary closed-loop and ERRORs on scripted input
- t6_owned_chop: declared scripted control (allowed, non-critical). owned-mother discretionary-chop NEGATIVE control: proves detector D-8 can FAIL (its detectors.json records the designed D-8 FAIL); never cited as evidence that an invariant holds

## single-model - CLEAR

### Notes

- CONVERSION_RACE_ORACLE: importer verified: ../banana-restoration-r2/trace_detectors.py
- CONVERSION_RACE_ORACLE: importer verified: ../banana-restoration-r2/regression_tests.py
- CONVERSION_RACE_ORACLE: mirror accepted: ../banana-restoration-r2/banana_blocks/block-i1.rs
- CONVERSION_RACE_ORACLE: mirror accepted: ../banana-restoration-r2/research-banana-r2.rs [NOTE: file never cites the oracle name CONVERSION_RACE_ORACLE; declared rationale: complete readable research source; arithmetic identity with the compact candidate (and hence with the cited block-i1 mirror) is established by the research-vs-compact replay-equality gate (gate-results-v4-2026-08-05.md) and the seam asserts of build_banana_candidate.py. Declared here so the mirror is visible; the file does NOT cite the oracle name in-text - see validation report finding]
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/trace_detectors.py:166: ceil(health / chop_power) claims four.
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/trace_detectors.py:1092: arrival-only comparison exact_chops < eta_opp_at_chop_start is
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/regression_tests.py:31: 2f58edef... (its voided max(eta_opp, predicted.cooldown) deadline refuses the
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/regression_tests.py:183: "rhs_deadline": max(eta_opp, ripen_proxy),
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/regression_tests.py:184: "accepts": eta_res + chops < max(eta_opp, ripen_proxy)},
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/regression_tests.py:284: flip and conversion is impossible (travel + ceil(health/chop_power)
- CONVERSION_RACE_ORACLE: explained hit (verified importer) ../banana-restoration-r2/regression_tests.py:494: "< max(eta_opp, predicted.cooldown)", D-8-old arrival-only) answers
- CONVERSION_RACE_ORACLE: ../banana-restoration-r2/regression_tests.py: 2 comment-only mention(s) (prose, not computation - not blocking)
- CONVERSION_RACE_ORACLE: ../banana-restoration-r2/make_banana_traces.py: 2 comment-only mention(s) (prose, not computation - not blocking)
- CONVERSION_RACE_ORACLE: explained hit (declared mirror) ../banana-restoration-r2/banana_blocks/block-i1.rs:694: Some(resident_eta + chop_turns - 1 < eta_opp.max(ripe))
- CONVERSION_RACE_ORACLE: ../banana-restoration-r2/banana_blocks/block-i1.rs: 4 comment-only mention(s) (prose, not computation - not blocking)
- CONVERSION_RACE_ORACLE: explained hit (declared mirror) ../banana-restoration-r2/research-banana-r2.rs:2611: Some(resident_eta + chop_turns - 1 < eta_opp.max(ripe))

## red-reason - CLEAR

### Notes

- R-1-vs-f29efd0e: RED for the right reason on git:a787d478:claude_1/banana-restoration-r2/candidate-banana-r2.min.rs (exit 1, all 4 signature regexes matched)
- R-3b-vs-280ed777: RED for the right reason on git:0ece10ec:claude_1/banana-restoration-r2/candidate-banana-r2.min.rs (exit 1, all 4 signature regexes matched)
- R-3b-vs-2f58edef: RED for the right reason on git:8b000bad:claude_1/banana-restoration-r2/candidate-banana-r2.min.rs (exit 1, all 4 signature regexes matched)
- R-4-vs-2f58edef: RED for the right reason on git:8b000bad:claude_1/banana-restoration-r2/candidate-banana-r2.min.rs (exit 1, all 4 signature regexes matched)
- R-5-vs-9f5ef833: RED for the right reason on git:b358124f:claude_1/banana-restoration-r2/candidate-banana-r2.min.rs (exit 1, all 5 signature regexes matched)

## claims-coverage - CLEAR

### Notes

- critical invariant I-9: 2 non-scripted evidence entr(y/ies) present
- critical invariant I-10a: 3 non-scripted evidence entr(y/ies) present
- critical invariant I-7: 2 non-scripted evidence entr(y/ies) present
- critical invariant D-8: 1 non-scripted evidence entr(y/ies) present
- critical invariant I-19: 1 non-scripted evidence entr(y/ies) present
- critical invariant I-20: 1 non-scripted evidence entr(y/ies) present
- critical invariant I-21: 1 non-scripted evidence entr(y/ies) present
- required deliverable present: ../banana-restoration-r2/candidate-banana-r2.min.rs
- required deliverable present: ../banana-restoration-r2/research-banana-r2.rs
- required deliverable present: ../banana-restoration-r2/candidate-banana-r2-manifest.json
- required deliverable present: ../banana-restoration-r2/build_banana_candidate.py
- required deliverable present: ../banana-restoration-r2/conversion_race_oracle.py
- required deliverable present: ../banana-restoration-r2/invariant-spec-2026-08-04.md
- required deliverable present: ../banana-restoration-r2/regression_tests.py
- required deliverable present: ../banana-restoration-r2/trace_detectors.py
- required deliverable present: ../banana-restoration-r2/gate-results-v4-2026-08-05.md
- required deliverable present: ../banana-restoration-r2/red-evidence-2f58edef-2026-08-05.md
- ledger class VACUOUS_EVIDENCE: covered by configured check claims-coverage
- ledger class SCRIPTED_TRACE: covered by configured check trace-provenance
- ledger class MODEL_DIVERGENCE: covered by configured check single-model
- ledger class RED_WRONG_REASON: covered by configured check red-reason
- ledger class MULTI_UNIT_COORDINATION: covered by configured check red-reason
- ledger class INSTRUMENT_GAP: checklist-detected; answer on file: The static-opponent gap named in r1 was closed by the dynamic-opponent referee (make_banana_traces DYNAMIC_SCENARIOS t3/t4 and the R-4 scenario, where the opponent harvester really approaches and captures). Multi-unit OWN-side coordination - deferred to the host replay gate through round 4, which the round-4 host review rejected as a deferral (its finding 1 is exactly such a failure) - is now locally expressible: the R-5 scenario (scenario_r5_two_worker_banking, CustomMapReferee) runs both own workers closed-loop with the full carrier's bank route crossing the protected cell, and the R-5-vs-9f5ef833 pair mechanizes the MULTI_UNIT_COORDINATION ledger class. Remaining inexpressible classes: multi-unit OPPONENT coordination and platform-engine tie-breaking order; both remain covered only by the integrator's host replay gates and are declared, not hidden.
- ledger class SPEC_TEST_GAP: covered by configured check claims-coverage
- ledger class UNSAMPLED_STATE_SPACE: covered by configured check fuzz-panel
- ledger class MISSING_DELIVERABLE: covered by configured check claims-coverage

## fuzz-panel - BLOCK

### Findings (blocking)

- **UNSAMPLED_STATE_SPACE** `fuzz-panel`: external check reports BLOCK (exit 1); an external BLOCK is a pre-review BLOCK. Output tail: fuzz_panel: BLOCK (240 games, 47 blocking, 89 flagged, 11.4 s; report: ../banana-restoration-r2/fuzz/fuzz-report-latest.md)

---

**VERDICT: BLOCK** - blocking findings above; the handoff must not proceed
