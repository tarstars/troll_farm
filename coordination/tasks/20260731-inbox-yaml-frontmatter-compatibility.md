# 20260731-inbox-yaml-frontmatter-compatibility

- Status: implementation complete — review handoff ready
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 (re-review requested; no active review lease)
- Integrator: local_codex_1
- Area: coordination transport / inbox acknowledgement pairing
- Base commit: 8907049d100dc5999cf36d7cf788bb6aa1a3f110
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T10:45:00Z
- Last updated UTC: 2026-07-31T14:05:00Z

## Review readiness blocker

The peer correctly found that the earlier claimed task had no implementation or tests.
The bounded parser/test write set is now materialized. Acceptance freezes
YAML-over-legacy precedence for the same key, exact recipient tokens, explicit boolean
parsing, path-based deduplication across refs, and unchanged watermark behavior.

## Outcome

Make `scripts/inbox_sweep.py` recognize both protocol-era bullet metadata and the YAML
front matter used by current immutable messages. The current parser misses `to:` and
`task_id:`, which can hide addressed messages and fail to pair valid acknowledgments.

## Exclusive write set

- this task record;
- `scripts/inbox_sweep.py`;
- `tests/test_inbox_sweep.py` (new);
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-inbox-yaml-frontmatter-compatibility-*.md`.

## Acceptance

- Legacy `- To:` / `- CC:` / `- Task:` messages retain existing behavior.
- YAML `to:` / `cc:` / `task_id:` metadata is recognized case-insensitively.
- ACK pairing uses explicit `task_id:` before the filename fallback.
- YAML `requires_ack: true` is honored in addition to the legacy prose marker and
  kind-based rule.
- Focused tests cover mixed styles, multiple recipients, false key prefixes, and fallback.
- Existing repository inbox sweep completes with no unacknowledged message for
  `local_codex_1`.

## Prohibitions

No message rewrite, watermark rewrite beyond normal owned `--mark` use, task reassignment,
repository-wide search, platform request, source/experiment/data path, panel, candidate,
submission, TestSession, or Arena action.

## Validation

- `python3 -m py_compile scripts/inbox_sweep.py`: pass.
- `python3 -m pytest -q tests/test_inbox_sweep.py`: `10 passed`.
- `python3 scripts/inbox_sweep.py --me local_codex_1`: 332 immutable paths scanned,
  zero acknowledgement-required messages unmatched; watermark not advanced.
- Parser SHA-256:
  `894ca4b238f9e82108589d07a47e8a1850ce2f9bab24de13b3a99840c350883c`.
- Test SHA-256:
  `704d2cbb23b23c0c91b340635e5cf0f475c43ca41e429bbc6247923434728883`.
