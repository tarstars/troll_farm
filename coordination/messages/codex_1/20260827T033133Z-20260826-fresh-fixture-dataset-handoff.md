---
schema_version: 2
type: handoff
task_id: 20260826-fresh-fixture-dataset
from: codex_1
to: ["claude_1"]
cc: ["local_claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/codex_1/20260827T033133Z-20260826-fresh-fixture-dataset-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260827T024113Z-20260826-fresh-fixture-dataset-update.md", "coordination/messages/local_claude_1/20260827T032219Z-20260826-fresh-fixture-dataset-handoff.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: c0a4074dec04090c943738e2fc60c37c31abed9c
artifact_paths: ["scripts/cut_fixtures.py", "tests/test_cut_fixtures.py", "codex_1/fixtures/champion-v6-72673124-2026-08-27.json", "codex_1/fixtures/keep-v6-04e3db43-2026-08-27.json", "codex_1/fixtures/first-library-report-2026-08-27.md"]
created_utc: 2026-08-27T03:31:33Z
---

- To: claude_1
- CC: local_claude_1, user, chatgpt_1
- Task: 20260826-fresh-fixture-dataset
- Requires acknowledgement: yes — this is the one chartered review handoff

# handoff: fresh real-game fixture generator and first bot-hash-tagged libraries

The deterministic 212-game slice was hash-verified before decoding. The champion plus
version-6 telemetry library contains 29 parked-troll windows and 139 blocked-troll windows;
the keep-rule plus version-6 library contains 8 blocked-troll windows. Both generated
libraries pass the grading harness, and the two detector unit tests pass.

All required classes carry counts, including zeroes. Dance, 60-turn stall, and long-kept-goal
events are absent from this slice. The turn-100 shack-engine-start predicate is explicitly
unavailable because version-6 telemetry does not expose referee-success ownership or that
engine-start predicate; the generator refuses to infer it from a proxy. These are slice counts,
not population prevalence.

Please perform the one review budgeted by the charter. Review the deterministic manifest/hash
checks, replay-derived seat handling, detector definitions, regeneration rule, zero-class
reporting, and whether the grading mode is sufficient for the harness to consume the library.

Validation:

```text
uv run pytest -q tests/test_cut_fixtures.py
2 passed

uv run python scripts/cut_fixtures.py --grade codex_1/fixtures/champion-v6-72673124-2026-08-27.json
PASS

uv run python scripts/cut_fixtures.py --grade codex_1/fixtures/keep-v6-04e3db43-2026-08-27.json
PASS
```
