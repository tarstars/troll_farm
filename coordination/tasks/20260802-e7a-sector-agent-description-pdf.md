# 20260802-e7a-sector-agent-description-pdf: document the live sector agent

- Status: handoff_ready
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: pending
- Integrator: local_codex_1
- Area: E7a documentation
- Base commit: 268eca6d8159123c03e235565757c3cc7fefca78
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-08-02T19:10:58Z
- Last updated UTC: 2026-08-02T19:16:08Z

## Outcome

A detailed, rendered PDF describing the exact live E7a sector agent: inherited algorithms,
the 95-byte map-sector modification, design ideas, evidence, and limitations.

## Frozen protocol

None. Documentation only; experiment and live measurements remain governed by their
existing records.

## Exclusive write set

- `docs/reports/2026-08-02-e7a-sector-agent-description.md`
- `docs/reports/2026-08-02-e7a-sector-agent-description.tex`
- `docs/reports/2026-08-02-e7a-sector-agent-description.pdf`
- `coordination/tasks/20260802-e7a-sector-agent-description-pdf.md`
- `coordination/messages/local_codex_1/*20260802-e7a-sector-agent-description-pdf*`
- `coordination/status/local_codex_1.md`

## Shared read-only paths

- Exact stable parent and E7a candidate under `cgauto/submissions/`
- E7a manifest, bridge, pricing, and Arena execution records
- `docs/STATE.md`, `docs/CONSTRAINTS.md`, and live ledger

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred)
- `cgauto/submissions/` (immutable)
- raw game cache, cron, and sealed map ranges

## Deliverables

- Detailed Markdown source, XeLaTeX source, and rendered PDF.
- Exact candidate/parent hashes, source-size delta, live submission identity, and evidence boundary.
- Full controller pipeline, sector rule, design rationale, evidence, and failure profile.

## Acceptance checks

- `xelatex` completes twice without errors.
- `pdfinfo` reports a non-empty multi-page PDF.
- `pdftotext` contains the exact agent id, submission id, and both source hashes.
- Sacred source and raw-game cache remain unchanged.

## Arena authority

Read-only platform access: not needed. Platform mutation: forbidden/not needed.

## Handoff

Five-page Markdown/XeLaTeX/PDF package rendered and validated. PDF is 71,946 bytes,
SHA-256 `9ee104f47ae00344df2bdea7a8958d2e729385fc871ed7a3e87ab8de1d4c64e9`.
