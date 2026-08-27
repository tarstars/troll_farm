---
schema_version: 2
type: handoff
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260827T035442Z-20260826-fresh-fixture-dataset-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260827T034701Z-20260826-fresh-fixture-dataset-integrated.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: af0aec888390be8464ec0c5416cf6cbad666a376
artifact_paths: ["scripts/cut_fixtures.py", "tests/test_cut_fixtures.py", "codex_1/fixtures/champion-v6-72673124-2026-08-27.json", "codex_1/fixtures/keep-v6-04e3db43-2026-08-27.json", "codex_1/fixtures/first-library-report-2026-08-27.md"]
created_utc: 2026-08-27T03:54:42Z
---

- To: local_claude_1, claude_1
- CC: user
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes

# DELIVERY — the accepted fresh fixture library is ready for integration

I applied review edits 1–5 and the supported-decoder clarification. No accepted count changed:

- blocked fixtures remain per-turn windows for compatibility, with independent run counts now
  published beside them: champion **45 runs / 139 windows**, keep-rule **4 / 8**;
- the libraries now record matched, decoded, zero-telemetry, and row totals; all 212 matched games
  decode, zero games lack telemetry, and the arms contain 56,288 and 1,200 rows;
- champion keep-only classes are labelled inapplicable, dance is labelled without a real positive
  control, the stall/parked overlap is explicit, and the four-game keep sample is held pending the
  offered second slice;
- consumers are directed to `scripts.cut_fixtures.decode`.

I declined only optional edit 6, strengthening `--grade` against a hand-edited library. Generation
already pins the manifest and replay hashes, and this optional change affects no chartered count.

Validation at the pinned commit:

```text
uv run pytest -q tests/test_cut_fixtures.py                                      3 passed
uv run python scripts/cut_fixtures.py --grade ...champion...json                PASS
uv run python scripts/cut_fixtures.py --grade ...keep...json                    PASS
```

This is the final delivery under the one-review budget. Coordinator: integrate the five artifact
paths and close board row 0-3. No replacement card remains for codex_1.
