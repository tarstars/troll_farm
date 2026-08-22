# pre_review report - HISTORICAL round-3 rejected state (8b000bad / 2f58edef): t5 declared candidate-driven

- config: `config-a.json`
- checks run: trace-provenance

## Per-check verdicts

| check | verdict | findings |
|---|---|---|
| trace-provenance | BLOCK | 1 |

## Ledger class coverage

| class | mechanism | status this run |
|---|---|---|
| VACUOUS_EVIDENCE | claims-coverage | check not run (--only) |
| SCRIPTED_TRACE | trace-provenance | BLOCK (1 finding(s)) |
| MODEL_DIVERGENCE | single-model | check not run (--only) |
| RED_WRONG_REASON | red-reason | check not run (--only) |
| INSTRUMENT_GAP | checklist | n/a (adversarial pre-review) |
| SPEC_TEST_GAP | claims-coverage | check not run (--only) |
| MISSING_DELIVERABLE | claims-coverage | check not run (--only) |

## trace-provenance - BLOCK

### Findings (blocking)

- **SCRIPTED_TRACE** `t5_flip_convert-as-handed-off`: declared candidate-driven but the committed commands do not survive regeneration from the declared source (/tmp/banana-r3-state/candidate-banana-r2.min.rs): 17 of 20 command lines diverge (regenerated 20 lines). First 5: line 1: committed 'PICK 0 BANANA;WAIT' vs regenerated 'MSG yamo-carry-regen-transit-idle-harvest-rust;PICK 0 BANANA;WAIT'; line 4: committed 'MOVE 0 2 1;WAIT' vs regenerated 'WAIT;WAIT'; line 5: committed 'WAIT' vs regenerated 'WAIT;WAIT'; line 6: committed 'WAIT' vs regenerated 'WAIT;WAIT'; line 7: committed 'WAIT' vs regenerated 'WAIT;WAIT'

---

**VERDICT: BLOCK** - blocking findings above; the handoff must not proceed
