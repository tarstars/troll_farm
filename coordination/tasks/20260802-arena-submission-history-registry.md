# 20260802-arena-submission-history-registry

- Status: backlog-ready — unassigned
- Record owner: local_codex_1
- Work owner: unassigned / claimable
- Reviewer/integrator: local_codex_1
- Area: Arena operational evidence and deployment selection
- Created UTC: 2026-08-02T06:31:43Z
- Priority: P0 operational safety; complete before the next non-emergency candidate selection

## Incident and objective

The 2026-08-02 “best bot” selection searched the recent owner-directed lineage and chose the
far-denial source from one 22.99/160 terminal run. It failed to compare the complete source
history, where the exact stable preseed resident had repeated mature observations at 24.4,
24.1/142, and 23.05/171. Repeating far-denial then terminated at 19.37, rank 73/130.

Create a canonical machine-queryable history of bot artifacts, Arena submissions, observations,
relationships, and dispositions. A pre-submission query must make it difficult to repeat a
lineage-scoped or single-maximum selection error.

## Proposed deliverables

- `data/analysis/arena-submission-history.json` — schema-versioned generated projection;
- `cgauto/submission_history.py` — build, validate, and query commands;
- focused tests under `tests/` or the existing `cgauto` test convention;
- a compact schema/query note under `docs/`;
- provenance coverage report listing included, ambiguous, and unrecoverable historical runs.

The immutable checkpoints, execution reports, manifests, and platform reads remain sources of
truth. The JSON registry is reproducibly generated from an explicit input manifest; do not
silently scrape every file or make the derived projection the only copy of evidence.

## Required category axes

Every artifact/submission supports controlled enums plus optional free tags. Categories are
multi-axis: one flat label must not conflate strategy, lifecycle, and evidence quality.

### Strategy / architecture

- baseline controller family;
- economy, planting, harvest, and conversion;
- denial and opponent-resource targeting;
- movement, coordination, banking, and deadlock repair;
- workforce and training;
- search / rollout;
- learned policy or value model;
- packaging, slimming, runtime, or parity-only;
- composite / other, with explicit component relations.

### Deployment purpose

- stable resident or fallback;
- same-source capacity/A-A control;
- frozen-protocol qualified candidate;
- owner-directed live experiment;
- incident fix;
- safety restore;
- packaging/parity resubmission;
- unknown historical purpose.

### Evidence maturity

- cold start;
- provisional;
- mature;
- later-confirmed;
- terminal;
- invalid/identity-contaminated/unidentifiable.

### Disposition

- active;
- promoted;
- retained;
- restored;
- rejected;
- failed;
- displaced/superseded;
- pending/unknown.

### Comparison and authority

- same-source repeat, same-era control, A/A, candidate-vs-control, cross-era historical, or
  incomparable;
- frozen-qualified, owner-directed override, standing restore authority, emergency action,
  or unknown;
- explicit parent submission, replaced-by submission, source-derived-from, and same-source
  relationships.

## Minimum record fields

- stable schema version and record id;
- exact source path, bytes, SHA-256, language, recoverability, and source-family id;
- submission id, agent id, deployment timestamp, replacing/replaced ids, and task/protocol id;
- categories from every required axis;
- each observation's timestamp, games finished/pending, score, rank, field size, wins/ties/losses,
  mean margin, catastrophe count/rate, negative-margin mass, runtime/identity faults, and evidence
  path/hash;
- population context: ladder/division, pool time/size, score update time when available, and a
  comparability classification;
- final disposition, rationale, and provenance links.

Missing facts are explicit `null`/`unknown`; they are never guessed from filenames or a later
active row.

## Required queries

```text
build
validate
timeline
current
source --sha256 <sha>
submission --id <id>
compare-source <sha-or-family> [<sha-or-family> ...]
best --min-finished <n> --evidence mature --scope all
preflight <candidate-source-path>
```

Default `best` is source-level, not run-level: show repeated mature runs, median/range/worst,
recency and comparability warnings. Never rank solely by the maximum historical score. Any
lineage/category filter must be printed prominently and `preflight` must always include the
unfiltered all-history comparator table.

## Acceptance

1. Deterministic rebuild and byte-identical output from the frozen explicit input manifest.
2. Unique submission and agent identities; source groups keyed by exact SHA-256.
3. Every known deployment from the restored resident era onward is covered or appears in an
   explicit unresolved list; older recoverable controls are included.
4. Historical regression fixture proves that an all-history preflight for far-denial shows:
   - preseed resident mature observations 24.4, 24.1/142, and 23.05/171;
   - far-denial mature repeats 22.99/160 and 19.37/160;
   - a warning against selecting far-denial from its 22.99 maximum alone.
5. Queries distinguish current live measurements, historical measurements, and projections.
6. Invalid/partial/identity-mismatched checkpoints cannot be promoted to mature evidence.
7. `preflight` emits source hash/size, prior deployments of that exact hash, stronger historical
   source families, evidence gaps, and the category/lineage scope used.
8. Unit tests cover duplicate ids, conflicting hashes, missing provenance, cross-era comparison,
   category validation, deterministic ordering, and the regression above.

## Boundaries

Read-only repository and platform inspection only. No Arena mutation, source edit, history
rewrite, secret/session serialization, raw-game mutation, sealed-range read, broad filesystem
search, or external-storage migration. Scope file discovery to an explicit tracked-file manifest;
never scan the large sibling workspaces.
