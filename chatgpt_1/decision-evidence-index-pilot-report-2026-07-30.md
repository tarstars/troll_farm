# Decision-evidence index pilot — implementation report

Prepared UTC: 2026-07-30T18:05:00Z  
Task: `20260730-decision-evidence-index-pilot`  
Work owner: `chatgpt_1`  
Reviewer/integrator: `local_codex_1`  
Branch: `agent/chatgpt_1-evidence-index-pilot`  
Base shared head: `f1f3292cfe4cfd35e006c9f8ae7f2ffe4de23dc0`

## Delivered architecture

The pilot treats each human-reviewed Markdown record as canonical. An embedded
`DECISION-EVIDENCE-JSON` block is part of that record and is the only machine input.
Generated YAML-compatible JSON, the navigation index, the CONSTRAINTS projection, the
equivalence report, and the manifest are deterministic projections and are not edited by
hand.

The schema mechanically requires scope, conclusion, `does_not_prove`, limitations,
reopening conditions, relations, cost, evidence strength, explicit populations for numeric
claims, and repository evidence locators. `void-premise` is a first-class status with a
required premise/refutation block and is excluded from closure counts. Ladder-effect claims
must be backed by `arena_measured` evidence or explicitly labelled as projections.

## Pilot inventory

Ten required records plus a real H7 `void-premise` record are included:

1. `D30` — generated-map substrate invalidation;
2. `D101` — observational architecture diagnosis;
3. `D161` — exact-resident substrate dominance rule;
4. `D169` — positive hindsight option envelope;
5. `D172a` — definitive selector-learning closure;
6. `D175a` — controlled harmful early-planting mechanism;
7. `H1` — conditional accounting closure;
8. `D176a` — successful mechanism, immaterial value, and gate-design error;
9. `OWNER-GOAL-20260730` — goal re-scope;
10. `OWNER-ARENA-20260730` — standing Arena policy;
11. `H7` — false body-blocking premise, excluded from closures.

Two stable discussion records preserve unresolved scope questions: `D101-Q1` and `H1-Q1`.
The generated index reports 11 records, six scientific closures/invalidations, and one
void-premise record.

## Equivalence result

Nine scientific/hypothesis records map to existing `docs/CONSTRAINTS.md` bullets with the
same scope and binding decisive numbers. The two owner decisions have no matching
CONSTRAINTS bullet; their binding source is `docs/STATE.md`, and the equivalence report
marks this absence rather than inventing a match.

D176a is represented without flattening its mixed result:

- mechanism: successful;
- value: immaterial (`+0.045`, CI `[−0.024,+0.114]`);
- protocol quality: gate-design error (real-corpus 133-turn threshold versus panel-control
  247 turns, plus an inherited 5–9-turn gate that did not identify the intended mechanism).

## Validation commands and results

Commands executed:

```bash
python3 -m py_compile \
  cgauto/build_decision_evidence_index.py \
  cgauto/check_decision_evidence_index.py
python3 cgauto/build_decision_evidence_index.py
python3 cgauto/check_decision_evidence_index.py
python3 -m pytest -q tests/test_decision_evidence_index.py
python3 cgauto/build_decision_evidence_index.py --check
```

Results:

```text
{"closures_excluding_void": 6, "records": 11, "status": "ok", "void_premise": 1}
23 passed
```

The 23 focused tests include malformed fixtures for required fields, cost, evidence
strength, missing/unsafe paths, line ranges, JSON pointers, relations, discussion IDs,
population compatibility, ladder-evidence discipline, `void-premise`, D176a's three-way
result, closure counting, and deterministic generation.

Generated SHA-256 values:

- `decision-evidence-index.yaml`: `308bb3dccf07b4a46617e48336fa576a421c87951bece1e5b46c415d1e084481`
- `DECISION-EVIDENCE-INDEX.md`: `6860ba71b17202d4a7096d71011d2d21e2f566d0e5223179db3a4cff98c10453`
- `CONSTRAINTS-PILOT-PROJECTION.md`: `4a9b1e04fd64a2526180050a2a538b7ab01bbeac0d4aa7d1b14b12142d8b3809`
- `equivalence-report.md`: `b418781eb01057be06a97625b13eb5e0c671e2dd82e8b174c814bd92f0a42004`

## Execution limitation and reviewer action

This agent runtime does not contain a real repository checkout. Source-path existence, the
four referenced repository files, all cited line ranges, and both exact JSON-pointer values
were verified against canonical `main` through the GitHub connector. The full checker was
then run against a local path mirror containing those verified sources. This establishes the
pilot's internal and locator logic but is not a substitute for a final execution in the
reviewer's actual checkout.

Before accepting/merging, the reviewer should run the exact commands above on the branch.
Any actual-checkout path, line-range, JSON-pointer, generation, or equivalence failure is a
blocker and must not be waived in prose.

## Safety and scope

No existing CONSTRAINTS, STATE, BACKLOG, ledger, frozen protocol/result, resident source,
raw/sealed data, submission tool, or Arena state was changed. The generated CONSTRAINTS
projection is explicitly non-authoritative. This pilot authorizes neither bulk migration nor
PDF generation.
