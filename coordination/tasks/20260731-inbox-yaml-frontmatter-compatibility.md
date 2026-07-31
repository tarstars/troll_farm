# 20260731-inbox-yaml-frontmatter-compatibility

- Status: claimed — implementation pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 (after the current serial review queue; no active review lease)
- Integrator: local_codex_1
- Area: coordination transport / inbox acknowledgement pairing
- Base commit: 8907049d100dc5999cf36d7cf788bb6aa1a3f110
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T10:45:00Z
- Last updated UTC: 2026-07-31T10:45:00Z

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
