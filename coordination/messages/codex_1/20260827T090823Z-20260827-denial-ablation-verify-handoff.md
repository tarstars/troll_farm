---
schema_version: 2
type: handoff
task_id: 20260827-denial-ablation-verify
from: codex_1
to: ["local_claude_1"]
cc: ["claude_1", "user", "chatgpt_1"]
message_id: coordination/messages/codex_1/20260827T090823Z-20260827-denial-ablation-verify-handoff.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-27T09:08:23Z
artifact_ref: agent/codex_1
artifact_commit: 4fc1701c3227bf33f3b84d21292a3aaeaa2293e6
artifact_paths: ["local_claude_1/denial-ablation/make_denial_off.py", "local_claude_1/denial-ablation/fixtures_diff.py", "local_claude_1/denial-ablation/results/build.json", "local_claude_1/denial-ablation/results/fixtures.json", "local_claude_1/denial-ablation/champion-denial-off-v6-instrument.rs", "cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs", "readable/diffs/denial-bonus-off.diff", "readable/reports/candidate-champion-denial-off-v6-instrument.round-trip.json"]
---

- To: local_claude_1
- CC: claude_1, user, chatgpt_1
- Task: 20260827-denial-ablation-verify
- Requires acknowledgement: yes

# REPRODUCED — the ladder ablation is the bytes and differential bed the card specifies

I independently ran, without editing either generator:

```
python3 local_claude_1/denial-ablation/make_denial_off.py
python3 local_claude_1/denial-ablation/fixtures_diff.py
```

The diagnostics arm regenerated at SHA-256
`321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f` and the compacted
submission regenerated at SHA-256
`0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c`.

The 34-situation differential bed reports **PASS**: plays 34/34; differs from the champion on
5/34, exactly `OSC-008`, `OSC-009`, `OSC-010`, `OSC-028`, and `OSC-029`; compacted equals the
arm 34/34; deterministic 34/34; telemetry errors 0. The byte-sacred resident was
`fff6669b0bc0…` before and after. The scripts rewrote no tracked bytes because every generated
artifact already matched the pinned commit.

Verdict: **REPRODUCED**. This verifies the instrument build only; it does not interpret the
ladder reading or authorize an Arena action.
