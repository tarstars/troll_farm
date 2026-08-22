# pre_review report - HISTORICAL round-3-era instruments (8b000bad): single-model vs CONVERSION_RACE_ORACLE

- config: `config-b.json`
- checks run: single-model

## Per-check verdicts

| check | verdict | findings |
|---|---|---|
| single-model | BLOCK | 11 |

## Ledger class coverage

| class | mechanism | status this run |
|---|---|---|
| VACUOUS_EVIDENCE | claims-coverage | check not run (--only) |
| SCRIPTED_TRACE | trace-provenance | check not run (--only) |
| MODEL_DIVERGENCE | single-model | BLOCK (11 finding(s)) |
| RED_WRONG_REASON | red-reason | check not run (--only) |
| INSTRUMENT_GAP | checklist | n/a (adversarial pre-review) |
| SPEC_TEST_GAP | claims-coverage | check not run (--only) |
| MISSING_DELIVERABLE | claims-coverage | check not run (--only) |

## single-model - BLOCK

### Findings (blocking)

- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/trace_detectors.py`: listed as allowed_importer of CONVERSION_RACE_ORACLE but no import statement matching '^\\s*(?:import\\s+.*\\bconversion_race_oracle\\b|from\\s+.*\\bconversion_race_oracle\\b\\s+import\\b)' was found - its quantity references are unexplained
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/regression_tests.py`: listed as allowed_importer of CONVERSION_RACE_ORACLE but no import statement matching '^\\s*(?:import\\s+.*\\bconversion_race_oracle\\b|from\\s+.*\\bconversion_race_oracle\\b\\s+import\\b)' was found - its quantity references are unexplained
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/block-i1.rs`: declared mirror of CONVERSION_RACE_ORACLE lacks the required marker 'CONVERSION_RACE_ORACLE' - an unmarked mirror is indistinguishable from a divergent reimplementation
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/trace_detectors.py:162`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'ceil\\w*\\(\\s*(?:current_)?health\\b[^)]*chop') in a file that is neither a verified importer nor a declared mirror: ceil(health / chop_power) claims four.
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/trace_detectors.py:1119`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'exact_chops\\w*\\s*<\\s*eta_opp') in a file that is neither a verified importer nor a declared mirror: race_won = exact_chops < eta_opp_now
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/regression_tests.py:193`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'ceil\\w*\\(\\s*(?:current_)?health\\b[^)]*chop') in a file that is neither a verified importer nor a declared mirror: flip and conversion is impossible (travel + ceil(health/chop_power)
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/regression_tests.py:245`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'ceil\\w*\\(\\s*(?:current_)?health\\b[^)]*chop') in a file that is neither a verified importer nor a declared mirror: ceil(health/chop_power) chop turns) completes strictly before eta_opp,
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/regression_tests.py:330`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'ceil\\w*\\(\\s*(?:current_)?health\\b[^)]*chop') in a file that is neither a verified importer nor a declared mirror: static ``chop_turns = ceil(current_health / chop_power)`` and the
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/regression_tests.py:331`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'max\\(\\s*(?:t\\s*\\+\\s*)?eta_opp') in a file that is neither a verified importer nor a declared mirror: ripen-proxy deadline ``max(eta_opp, cooldown)``, ignoring growth during
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/regression_tests.py:394`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'max\\(\\s*(?:t\\s*\\+\\s*)?eta_opp') in a file that is neither a verified importer nor a declared mirror: static_deadline = max(eta_opp_t0, ripen_proxy)
- **MODEL_DIVERGENCE** `/tmp/banana-r3-state/block-i1.rs:550`: quantity governed by CONVERSION_RACE_ORACLE computed outside the oracle (pattern 'eta_opp\\w*\\s*\\.\\s*max\\s*\\(') in a file that is neither a verified importer nor a declared mirror: Some(resident_eta + chop_turns < eta_opp.max(ripen))

### Notes

- CONVERSION_RACE_ORACLE: /tmp/banana-r3-state/regression_tests.py: 2 comment-only mention(s) (prose, not computation - not blocking)
- CONVERSION_RACE_ORACLE: /tmp/banana-r3-state/block-i1.rs: 4 comment-only mention(s) (prose, not computation - not blocking)

---

**VERDICT: BLOCK** - blocking findings above; the handoff must not proceed
