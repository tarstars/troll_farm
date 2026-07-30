# 20260730-decision-evidence-index-pilot: prove a reviewable decision/evidence schema

- Status: blocked in mandatory host validation — builder SyntaxError; correction requested
- Record owner: local_codex_1
- Work owner: chatgpt_1
- Reviewer: local_codex_1
- Integrator: local_codex_1
- Area: decision/evidence infrastructure pilot
- Base commit: 40b42502b2289d18835fe416a30129d48e30ceab
- Branch: agent/chatgpt_1-evidence-index-pilot (to be created and acknowledged by work owner)
- Progress lease: begins when the work owner publishes the execution acknowledgement/claim
- Created UTC: 2026-07-30T17:42:45Z
- Last updated UTC: 2026-07-30T18:54:04Z

## Outcome

A heterogeneous, mechanically validated pilot demonstrating that a reviewer can traverse
from a binding decision to its exact scope, evidence, numeric populations, limitations,
corrections, reopening rule, cost, and source artifacts without searching the repository.

The pilot succeeds only if its generated projection can reproduce the meaning and decisive
numbers of the corresponding `docs/CONSTRAINTS.md` bullets equivalently. It does not
replace or edit CONSTRAINTS during the pilot.

## Accepted authority and schema decisions

1. Canonical authority is the human-reviewed Markdown decision record. YAML, indexes, and
   graph views are deterministic generated projections checked for equivalence.
2. Granularity is one record per decision. Repair attempts sharing one frozen question and
   verdict are an attempt list inside one record.
3. Coverage includes every decision that binds future work: scientific, owner/governance,
   Arena/operations, programme authorization, storage, and history policy.
4. Accepted records are append-only. A correction is a new record/relation retaining the
   historical claim and naming what it corrects or supersedes.
5. Discussion records are repository Markdown with stable IDs; no GitHub dependency.
6. Every record includes `cost`.
7. Every numeric claim includes `population`, source path, and JSON path where available.
   Textual evidence includes a file and line range. External artifacts use a digest plus
   their repository-relative manifest, never a bare physical mount path.
8. Evidence strength distinguishes at least `mechanics_proof`, `panel_causal`,
   `arena_measured`, `observational_audit`, `accounting_model`,
   `public_source_statement`, and `inference_or_hypothesis`. Ladder-effect claims require
   `arena_measured` evidence or an explicit projection label.
9. `void-premise` is a first-class status, excluded from closure counts, with a required
   `premise_failure` block naming the false premise and refutation.
10. Mandatory scope fields include `does_not_prove`, limitations/counterevidence,
    correction/supersession relations, and reopening conditions.
11. A record is `proposed` on author publication and `accepted` only after integrator
    review/merge with the validator passing.

Binding review sources:

- `chatgpt_1/decision-evidence-index-review-proposal-2026-07-30.md`
- `coordination/messages/claude_1/20260730T070400Z-20260730-n1-violation-and-review-integrated.md`
- `coordination/messages/claude_1/20260730T124111Z-20260730-evidence-index-substantive-review-policy.md`
- `coordination/messages/chatgpt_1/20260730T162500Z-20260730-decision-evidence-index-review-ack.md`

## Pilot set

Create records for the proposal's deliberately heterogeneous set:

1. D30 — substrate invalidation;
2. D101 — observational architecture diagnosis;
3. D161 — resident-substrate dominance decision;
4. D169 — positive hindsight envelope;
5. D172a — definitive learning closure;
6. D175a — controlled harmful mechanism;
7. H1 — conditional accounting closure;
8. D176a — positive mechanism, immaterial value, and mis-specified gates;
9. owner goal re-scope — governance decision;
10. standing Arena authorization — operational policy.

Also include a validator fixture or minimal pilot record exercising `void-premise`
(`H7` is the preferred real example) so the required status is tested non-vacuously.

## Exclusive write set

- `chatgpt_1/` (pilot design notes, reports, and work-owner records)
- `docs/evidence/` (new canonical pilot records, discussions, schemas, and generated views)
- `cgauto/check_decision_evidence_index.py` (new)
- `cgauto/build_decision_evidence_index.py` (new, only if needed for deterministic projections)
- `tests/test_decision_evidence_index.py` (new)
- `coordination/status/chatgpt_1.md`
- `coordination/messages/chatgpt_1/`

No existing path in this set may be reformatted incidentally. If another new path is
required, publish a question and obtain an explicit write-set amendment first.

## Shared read-only paths

- `docs/CONSTRAINTS.md`
- `docs/STATE.md`
- `docs/BACKLOG.md`
- both live ledger volumes and `docs/D-series-atlas.pdf`
- frozen protocols, locks, result JSON/Markdown, decision messages, owner policies, and
  repository-relative artifact manifests needed by the pilot records

## Do not touch

- `docs/CONSTRAINTS.md`, `docs/STATE.md`, `docs/BACKLOG.md`, or any ledger volume
- the stale local 31-page PDF draft; do not commit or integrate it
- frozen protocols, locks, results, or existing immutable messages
- `rust/src/bin/yamo_orchard_live.rs`
- sealed ranges, `data/raw/games/`, or the 05:17 cron
- submission tooling, TestSession, Arena, or live platform state
- formatters over `rust/src/bin/` or `cgauto/`
- bulk migration beyond the explicit pilot set

## Deliverables

- canonical Markdown schema and ten pilot records under `docs/evidence/`;
- stable discussion records where a pilot decision has unresolved points;
- generated YAML/index projection and deterministic builder if required;
- mechanical validator and focused tests;
- `void-premise`, population-compatibility, evidence-strength, path/JSON-pointer, relation,
  discussion-ID, required-field, cost, and deterministic-generation checks;
- equivalence report showing how the pilot records regenerate the corresponding
  CONSTRAINTS claims without changing CONSTRAINTS;
- compact review handoff naming source commit, commands, row/record counts, hashes,
  limitations, and any schema question discovered.

## Acceptance checks

The work owner records exact final commands in the handoff. Minimum gates:

1. `python3 -m py_compile cgauto/check_decision_evidence_index.py` passes, plus the builder
   if it exists.
2. `python3 -m pytest -q tests/test_decision_evidence_index.py` passes.
3. The validator passes all pilot records and fails focused malformed fixtures for every
   mandatory rule.
4. Rebuilding generated projections twice is byte-identical and leaves `git diff --exit-code`
   clean for generated paths.
5. Every pilot numeric claim has an explicit population and resolvable evidence pointer.
6. Ladder-effect claims without `arena_measured` evidence are rejected unless marked as
   projections.
7. `void-premise` is excluded from closure counts and requires a populated
   `premise_failure`.
8. D176a can simultaneously express successful mechanism, immaterial value, and gate-design
   error without flattening any of them.
9. The equivalence report accounts for every matching CONSTRAINTS decisive number and
   scope; any mismatch is a blocker, not prose to waive.
10. No forbidden shared path changes, raw/sealed data access, or Arena action occurs.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden.

## Handoff

Publish the implementation commit, validator commands/results, deterministic-generation
hashes, pilot record inventory, equivalence report, and a review handoff to
`local_codex_1`. This pilot authorizes neither bulk migration nor final PDF generation.

## Host-validation blocker — 2026-07-30T18:54:04Z

The handoff at remote head `41b60b65ca9ddd35fb610f270cd48d578856d96c`
fails before validation: `cgauto/build_decision_evidence_index.py:108` contains a
backslash-bearing `.replace()` inside an f-string expression, producing
`SyntaxError: f-string expression part cannot include a backslash`. Compile, builder,
checker, and pytest collection therefore fail. The work owner has been asked to correct
and publish a new handoff; no pilot files are accepted or integrated yet.
