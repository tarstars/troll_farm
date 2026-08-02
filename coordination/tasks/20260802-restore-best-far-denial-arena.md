# 20260802-restore-best-far-denial-arena

- Status: submitted — clean initial health; read-only maturation monitoring
- Record owner: local_codex_1
- Work owner: local_codex_1
- Integrator: local_codex_1
- Arena controller: local_codex_1
- Area: owner-directed restoration of strongest mature Arena artifact
- Base commit: 7e0fec5c862fdf338cf5aaaf75be665d00a47dfb
- Branch: agent/local_codex_1
- Created UTC: 2026-08-02T05:42:33Z
- Last updated UTC: 2026-08-02T05:46:14Z

## Owner directive

> sent to the platform our curren the best bot

Interpret “current best” by mature Arena evidence, not source recency. Restore the exact
far-denial d3 artifact once.

## Selection evidence and preflight

- Current active funding-first agent/submission `6585846`/`41071360` has a fresh exact
  submission-scoped read: 265/265 parsed, score 16.37, rank 109/130, 40 catastrophes,
  negative mass 10,285, zero runtime signals, identity clean.
- Far-denial d3 agent/submission `6585578`/`41070584` terminated at 160/160 parsed,
  score 22.99, rank 34/113, 15 catastrophes, negative mass 3,801, zero runtime signals,
  identity clean. This is the strongest mature result among the current owner-directed
  lineage.
- Exact restore source:
  `cgauto/submissions/candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs`;
  63,033 bytes; SHA-256
  `307a07556ab79a3089995841575c07f4b001f2ea08ee5b13ff7586f0149c76cd`;
  sidecar exact.
- Read-only platform recovery proves the currently saved source is the expected
  funding-first artifact, 68,893 bytes, SHA-256 `b8382910…`.
- Sacred resident source remains byte-exact at SHA-256 `fff6669b…`.
- No other Arena controller or mutation is active; `claude_1` explicitly remains a
  non-controller and is blocked on credentials.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- own immutable coordination messages for this task and pending Claude acknowledgements;
- one new compact execution record/checkpoint under
  `data/analysis/live-agent-6553250/`;
- integrator-owned `docs/STATE.md`, `docs/BACKLOG.md`, and live-ledger disposition;
- exactly one `api_submit.py` call for the exact restore artifact, followed by read-only
  identity/health discovery.

## Stop conditions

Stop without retry on checksum/source mismatch, HTTP 422, ambiguous terminal response,
unexpected agent identity, concurrent mutation, or sacred-source drift. Do not touch sealed
ranges, raw games, cron, experiment sources, or unrelated working-tree changes.

## Result

- The exact source was submitted once; `TestSession/submit` returned HTTP 200 and
  submission `41079354`.
- New agent `6589510` owns ten exact matching battle rows.
- First health: 9/9 parsed, one pending, identity clean, zero runtime signals, score 0.0,
  rank 129/130, 4W/5L, mean margin +13.667, one catastrophe, negative mass 378.
- Platform mutation is terminal; monitoring is read-only.

Evidence:
`data/analysis/live-agent-6553250/owner-best-far-denial-restore-execution-2026-08-02.md`
and the exact submit log/checkpoint named there.

