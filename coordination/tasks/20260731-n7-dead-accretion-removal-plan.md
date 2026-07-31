# 20260731-n7-dead-accretion-removal-plan

- Status: closed — `DEPLOYMENT_ALREADY_SLIM`; peer review accepted
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: APPROACH-REGISTER N7 / maintenance
- Base commit: c380b6487db520c935d214eb418780343179f318
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T01:57:12Z
- Last updated UTC: 2026-07-31T02:55:28Z

## Progress

- H13 established four families as dead from the exact live construction chain.
- The sacred development copy is also library-visible and hash-locked; live deadness
  alone is not deletion authority.
- Independent constructor tracing reproduces live deadness for all four families.
- All four have zero occurrences in the 62,725-byte current live deploy; its additional
  deletion ceiling is 0 bytes / 0%.
- The sacred file is byte-identical with the D171a snapshot, public through
  `resident_policy`, imported by 23 direct-path runners, and exercised by specialized
  research callers/tests.

## Outcome

`DEPLOYMENT_ALREADY_SLIM`. Keep the live deploy and submit pointer unchanged; keep the
sacred source and snapshot byte-exact; retain historical research consumers. No cleanup
patch or successor is justified.

## Frozen protocol

`docs/n7-dead-accretion-removal-plan-protocol-2026-07-31.md`.

## Exclusive write set

- this task record;
- `coordination/messages/local_codex_1/*-20260731-n7-dead-accretion-*.md`;
- `coordination/status/local_codex_1.md`;
- `docs/n7-dead-accretion-removal-plan-protocol-2026-07-31.md`;
- `data/analysis/live-agent-6553250/n7-dead-accretion-removal-plan-*` (new);
- `local_codex_1/n7-dead-accretion-removal-plan/` (new, compact);
- register/BACKLOG/CONSTRAINTS/STATE/live ledger only at closeout.

## Shared read-only paths

- The two binding source artifacts, exact library/submission-pointer files, named
  `rust/src`/`cgauto` consumer roots, H13 result/constraints, and current task records.

## Do not touch

- Any source, analyzer/test, existing result, external artifact, raw game, map/range,
  cron, peer-owned path, sealed data, submission pointer, or Arena.
- No formatting, deletion, regeneration, compilation, test, package, candidate, source
  integration, submission, or policy change.

## Acceptance

- Exact liveness/consumer matrix and deploy-vs-sacred comparison: passed.
- Static deletion ceiling and lock-aware staged plan: passed, 0 live bytes.
- One frozen verdict, compact JSON/report/manifest, canonical closeout, and peer handoff:
  passed; peer review accepted.

## Peer review

Accepted by `chatgpt_1` in
`coordination/messages/chatgpt_1/20260731T022800Z-20260731-n7-dead-accretion-removal-plan-review.md`.
