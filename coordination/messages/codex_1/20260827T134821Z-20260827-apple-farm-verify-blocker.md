---
schema_version: 2
type: blocker
task_id: 20260827-apple-farm-verify
from: codex_1
to: ["codex_1"]
cc: ["local_claude_1", "claude_1", "user"]
message_id: coordination/messages/codex_1/20260827T134821Z-20260827-apple-farm-verify-blocker.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260827T134051Z-20260827-apple-farm-verify-handoff.md"]
supersedes: []
created_utc: 2026-08-27T13:48:21Z
---

- To: codex_1
- CC: local_claude_1, claude_1, user
- Task: 20260827-apple-farm-verify
- Requires acknowledgement: yes

# blocker: 0-5 build and bed reproduce; the prescribed smoke input is absent

DEFERRED: complete the one allowed apple-farm smoke run and publish the required verdict as soon as `data/processed/maps.jsonl` is reachable in this checkout or at the card's documented `/home/tarstars/prj/troll_farm/data/processed/maps.jsonl` fallback.

I ran the assignment on a clean branch rebased onto `origin/main` at `e04e0692211df3407eee245b13e5e136ec2d12fe`.

- Build REPRODUCED: arm sha256 `82c8ddd1347c8016aa80cdf883819e28ac867e7a193223f0c5311568d4833cf4`; compacted submission sha256 `8c6bc206417c6d22b593372ce42e74ce5698646c1f8a860073f349a2a082708c`, 66,082 bytes, readable diff +120 / -0, round-trip exact. Regeneration left tracked generated files byte-identical.
- Bed REPRODUCED: plays 34/34; differs from the champion 2/34 (OSC-026 turn 3, OSC-030 turn 1); deterministic 34/34; compacted == arm 34/34; telemetry errors 0.
- Smoke BLOCKED exactly at input open: neither documented path exists. Per the card, I stopped at step 2; I did not substitute a different corpus or edit the runner.
- Diff read: nothing in the insertion can make an own troll fell the farm tree or plant on the farm cell while the farm troll is away; `chop_candidates` excludes `farm_cell`, and `farm_candidates` is restricted to the harvest-capable lowest-id own unit.

This is not the requested REPRODUCED / NOT REPRODUCED verdict because the independent 24-map smoke has not run. It replaces the assignment with a visible queue item rather than silently closing incomplete work.
