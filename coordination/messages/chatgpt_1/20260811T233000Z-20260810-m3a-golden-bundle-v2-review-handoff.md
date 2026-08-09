---
schema_version: 2
type: handoff
task_id: 20260810-manifest-implementation
from: chatgpt_1
to: ["local_claude_1", "claude_1"]
cc: ["user", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260811T233000Z-20260810-m3a-golden-bundle-v2-review-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/chatgpt_1/20260810T163000Z-20260810-m3a-golden-bundle-review-handoff.md"]
artifact_ref: agent/chatgpt_1
artifact_commit: 50cc9bd8e767694bc0fbede4db8d13c5a2f60052
artifact_paths: ["chatgpt_1/m3a-golden-set-manifest-v2-2026-08-09.json", "chatgpt_1/m3a-d1-situation-library-2026-08-10.json", "chatgpt_1/m3a_verify_golden_set.py", "chatgpt_1/test_m3a_golden_set.py", "chatgpt_1/m3a-golden-bundle-renewal-2026-08-09.md", "chatgpt_1/verification/m3a-summary.txt", "chatgpt_1/verification/m3a-verifier.stdout.txt", "chatgpt_1/verification/m3a-tests.stdout.txt"]
created_utc: 2026-08-11T23:30:00Z
---

- To: local_claude_1, claude_1
- CC: user, local_codex_1
- Task: 20260810-manifest-implementation
- Requires acknowledgement: yes

# M3a golden bundle v2 renewed and green; external adoption reviews requested

The v1 bundle correctly represented the original base-panel population but its committed golden
JSON predated the extractor's `episode_ledger_sha256` field. GitHub Actions regenerated the JSON,
renewed every manifest pin together, made the bundle self-contained, and committed exact outputs.

Measured on the exact runner checkout:

```text
extractor exit: 0
byte comparison after renewal: 0
bundle verifier exit: 0
mutation/regeneration tests exit: 0
VERIFIED: 32 source-game situations / 34 D-1 episodes / 20 terminal-length episodes
```

Pins:

```text
golden JSON SHA-256:
774a1d337ebab8ecec5652d5c8d113c0c9c6f6fc9ef77258ffcf7438a961f911

manifest v2 SHA-256:
577b913b6abdc76e6b1b05a019b92157266209825d5b2d53610b692dea5d1742
```

The exact subject, detector contract, and source panel are now present on the canonical ref; the
manifest records all source, toolchain, test, and output bytes. The one-shot workflow and finalizer
were removed after their measured outputs were committed.

Requested reviews remain the original two different lenses:

- `local_claude_1`: fresh-checkout execution, exact regeneration, verifier, and every mutation test;
- `claude_1`: line-by-line cross-implementation review and reconciliation of the population and
  counting rules.

This handoff requests adoption review; it is not self-acceptance. The base-panel golden v2 and
Claude's separate c5 46-episode diagnostic library remain different versioned datasets.