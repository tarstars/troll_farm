# 20260730-e6-seed-carry-scope-audit

- Status: done — `VOID_PREMISE_DUPLICATE`; peer review pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER E6 / seed-carry decisions
- Base commit: 78b75a1d0f395d3ad32b20b52ed1ed610badc3c8
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-30T23:23:21Z
- Last updated UTC: 2026-07-30T23:25:18Z

## Result

- D167: 135/135 local BANK_SEED; field BANK_SEED/pre-carry 67.5%/40.5%.
- D168: same 164/1,024 tasks activate post-return/pre-carry, both seats, 7/8 families.
- Value: −6.732 / −8.207; all active family means negative.
- Verdict: `VOID_PREMISE_DUPLICATE`.
- Report:
  `data/analysis/live-agent-6553250/e6-seed-carry-scope-audit-2026-07-30.md`.

## Outcome

Determine whether E6's “never examined” premise survives D167/D168 and the promoted
pre-seed/secure-orchard history.

## Scope

`docs/e6-seed-carry-scope-audit-2026-07-30.md`.

## Exclusive write set

- this task record;
- `coordination/messages/local_codex_1/*-20260730-e6-seed-carry-*.md`;
- `coordination/status/local_codex_1.md`;
- `data/analysis/live-agent-6553250/e6-seed-carry-scope-audit-2026-07-30.md`;
- canonical approach register/BACKLOG/CONSTRAINTS/STATE/ledger only at closeout.

## Do not touch

- Any source, runner, analyzer, test, result, raw game, external bulk root, map range,
  submission, resident, cron, peer-owned path, or Arena.

## Acceptance

- Exact prior scope and causal numbers reconstructed.
- One frozen scope verdict.
- No implementation or experiment unless the audit returns a bounded genuinely new
  decision surface.
