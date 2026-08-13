# Decision-evidence pilot schema

Version: `2`

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

Every `source` is a git-pinned coordinate:

- `commit` — 40-character SHA. Hard error if it does not resolve; warning
  (`pending integration`) if it resolves but is not yet an ancestor of `origin/main`.
- `path` — repo-relative path as it existed at `commit`.
- exactly one of `locator` (`lines N-M`, interpreted at that commit) or `json_pointer`.
- `quote` — optional verbatim excerpt. Used only for the currency check: if it no longer
  appears in the *current* file, the validator warns. It never fails the build.

Hard errors on a source include: unresolvable commit; path absent at the pinned commit;
violating the exactly-one-of-`locator`/`json_pointer` rule; an invalid line range (`a<1` or
`b<a`); a line range out of bounds at that commit; a `json_pointer` source whose path is not
`.json`; an unresolved `json_pointer`; a `json_pointer` result that differs from a declared
`expected_value`; (for locator sources) claimed numeric tokens absent from the pinned excerpt;
and, for a citation of `docs/CONSTRAINTS.md`, an excerpt that does not identify the citing
record's id. These are build failures. This list is not exhaustive — malformed input (a
missing `source.path`, a non-40-character `commit`, an unparseable `locator` or `json_pointer`
string) also fails the build; `validate_source` in `cgauto/check_decision_evidence_index.py`
is the source of truth.

Line numbers are meaningless without their commit: `docs/CONSTRAINTS.md` is append-heavy and
every insertion shifts all citations below it. Pinning is what makes a citation permanent.

## Validation rules for claims

If a claim's `compared_population` differs from its `population`, the record must set
`population_compatibility` to either `invalid_disclosed` (which additionally requires
`incompatibility_reason`) or `transformed` (which additionally requires `population_transform`).

A record with `claims_ladder_effect` requires either a decisive claim of strength
`arena_measured`, or `projection_label: true`.

`void-premise` is a first-class status, excluded from closure counts, and requires a populated
`premise_failure` block containing `false_premise` and `refutation`. Conversely, `premise_failure`
is only valid on a `void-premise` record.

## Hypothesis tier

`docs/evidence/hypotheses/Q<n>.md` carries a `HYPOTHESIS-JSON` block with six required fields:
`id`, `question`, `origin` (exact v2 message paths), `positions` (agent + stance),
`status` (`open` / `investigating` / `resolved` / `void`), and `next_action`.

Entry cost is deliberately low — the 21-field record schema is the closing tax, not the entry
tax. A `resolved` hypothesis requires `graduated_to`, naming an existing record id; the
lightweight entry is never deleted, because the trail from question to answer is the product.
Hypothesis ids must be unique across `hypotheses/`, and every `origin` path must exist in the
repository — the same rot the git-pinned `source` coordinate abolishes for records applies here
too, just without a commit pin.

`generated/OPEN-QUESTIONS.md` is the backlog view. Like everything in `generated/`, it is
deterministic and must never be hand-edited.

## Generated projections

`build_decision_evidence_index.py` generates:

- `generated/decision-evidence-index.yaml` (JSON-compatible YAML);
- `generated/DECISION-EVIDENCE-INDEX.md`;
- `generated/CONSTRAINTS-PILOT-PROJECTION.md`;
- `generated/equivalence-report.md`;
- `generated/OPEN-QUESTIONS.md`;
- `generated/manifest.json`.

The projection is a review aid only and does not modify `docs/CONSTRAINTS.md`.
