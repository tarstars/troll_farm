# Decision-evidence pilot schema

Version: `1`

## Authority

Each file in `records/` is a canonical human-reviewed Markdown record. Its
`DECISION-EVIDENCE-JSON` block is part of that Markdown and is the only machine input.
Everything in `generated/` is deterministic and must never be edited by hand.

A proposed record becomes accepted only when the integrator merges it after the validator
and tests pass. Accepted records are append-only: corrections and supersessions are new
records with explicit relations.

## Required record fields

`schema_version`, `id`, `title`, `kind`, `status`, `decision_date`, `question`, `scope`,
`conclusion`, `primary_evidence_strength`, `cost`, `attempts`, `decisive_claims`,
`textual_evidence`, `does_not_prove`, `limitations`, `relations`, `reopening_conditions`,
`discussions`, `constraint_projection`, and `acceptance`.

Every numeric `decisive_claim` requires:

- a stable `name` and human `display`;
- an explicit `population`;
- an evidence `source.path`;
- either `source.locator` (`lines N-M`) or `source.json_pointer`;
- an allowed `evidence_strength`;
- `binding: true|false`.

If two populations are compared and differ, the record must either mark the comparison
`invalid_disclosed` with an explanation or declare a reproducible transformation.

A ladder-effect claim requires `arena_measured` evidence. Non-Arena estimates must set
`projection_label: true`.

`void-premise` is a first-class status, excluded from closure counts, and requires a
populated `premise_failure` block.

## Generated projections

`build_decision_evidence_index.py` generates:

- `generated/decision-evidence-index.yaml` (JSON-compatible YAML);
- `generated/DECISION-EVIDENCE-INDEX.md`;
- `generated/CONSTRAINTS-PILOT-PROJECTION.md`;
- `generated/equivalence-report.md`;
- `generated/manifest.json`.

The projection is a review aid only and does not modify `docs/CONSTRAINTS.md`.
