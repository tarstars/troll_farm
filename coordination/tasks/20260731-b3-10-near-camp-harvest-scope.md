# 20260731-b3-10-near-camp-harvest-scope

- Status: result ready — `CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`; peer review pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: BACKLOG B3.10 / near-camp opportunistic harvest
- Base commit: d1feacd8a198dcf5888080247ae5233e87b8d251
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T07:55:00Z
- Last updated UTC: 2026-07-31T08:10:00Z

## Result

- B3.8's 496 optimistic captures are individual fruit units across 205 games.
- Gross all-credit own-score ceiling: 2.4195/game.
- Gross factor-two deny-plus-capture ceiling: 4.8390 margin/game.
- The underlying walking-detour estimate omits HARVEST, DROP, and scheduling displacement.
- D173a/b both fail compact_gold, catastrophe, negative-mass, and mechanism gates.
- Scaling rationale is excluded by task and by D174a's live-bill correction.
- Verdict: `CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`.

Evidence:
`data/analysis/live-agent-6553250/b3-10-near-camp-harvest-scope-audit-result-2026-07-31.md`
and compact JSON beside it.

## Outcome

Decide whether B3.10 remains a scientifically distinct direct-fruit-value question after
B3.8, both D173 variants, D174a's live-bill correction, and the current experiment bar.
This is a scope audit, not an experiment proposal.

## Exclusive write set

- `coordination/tasks/20260731-b3-10-near-camp-harvest-scope.md`;
- `coordination/messages/local_codex_1/*-20260731-b3-10-near-camp-harvest-scope-*.md`;
- `coordination/status/local_codex_1.md`;
- `data/analysis/live-agent-6553250/b3-10-near-camp-harvest-scope-audit-result-2026-07-31.*`
  (new compact files);
- `local_codex_1/b3-10-near-camp-harvest-scope-audit/manifest.json` (new);
- integrator-owned canonical register/backlog/constraints/state/live-ledger updates only
  after the evidence verdict is fixed.

## Read-only evidence

- B3.8 near-camp event census in live ledger volume 2;
- D173a/D173b protocols, locks, results, and compact JSON;
- D174a and current live-bill correction;
- current STATE, CONSTRAINTS, BACKLOG, approach register, and live ledger tail.

## Acceptance

- Reconcile the 1,144 near-camp / 956 bill-relevant / 425 cheaply capturable counts.
- Separate “outside D173b's chop-shadow scope” from evidence that an independent safe
  action exists.
- Price only direct fruit value; never reuse the closed scaling rationale.
- Account for the trigger-independent compact_gold, catastrophe, negative-mass, and
  opportunity-cost failures both D173 arms exposed.
- Return exactly one:
  `CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`,
  `NARROWED_TO_EXACT_UNTESTED_INTERVENTION`, or
  `BLOCKED_INSUFFICIENT_PROVENANCE`.

## Prohibitions

No analyzer, source edit, frozen-artifact edit, raw/processed/bulk read, map/range, replay,
simulation, panel, tuning, candidate, submission, TestSession, or Arena action. Do not
open a successor protocol from this task.
