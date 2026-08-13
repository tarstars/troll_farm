---
schema_version: 2
type: handoff
task_id: 20260810-manifest-implementation
from: chatgpt_1
to: ["local_claude_1", "claude_1"]
cc: ["user", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260810T163000Z-20260810-m3a-golden-bundle-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 8d9f182e20c67fdecf2aa050283c1c27e141139b
artifact_paths: ["chatgpt_1/m3a_extract_from_panel.py", "chatgpt_1/m3a-d1-situation-library-2026-08-10.json", "chatgpt_1/m3a_verify_golden_set.py", "chatgpt_1/test_m3a_golden_set.py", "chatgpt_1/m3a-golden-set-manifest-2026-08-10.json", "chatgpt_1/m3a-golden-bundle-review-contract-2026-08-10.md"]
created_utc: 2026-08-10T16:30:00Z
---

# Handoff: scripts are now first-class reviewed members of the M3a golden bundle

The owner's question is adopted as a binding rule:

- the 34-episode JSON is the **golden data set**;
- the extractor, bundle verifier, and mutation tests are the **trusted golden toolchain**;
- the source panel, exact subject bot, and detector contract are pinned inputs;
- none may change independently of the others.

The manifest pins the exact Git blob of every member. The verifier checks all member bytes, regenerates the library through the pinned extractor, demands byte-identical output, checks semantic summary and provenance, and enforces the external-review fields. The tests cover deletion, duplication, episode-window edits, non-D1 source drift, output drift, multiplicity, and non-self-approval.

## Required reviews

`local_claude_1`: execute the full regeneration, verifier, and tests on a second checkout/machine and publish the complete output. Confirm no skips.

`claude_1`: perform the cross-implementation, line-by-line method review of the extractor, verifier, and tests. Reconcile D-1-only/game-row counting against the separately published mixed-source/geometry-deduped library. Reviewing only the generated JSON is insufficient.

Commands:

```text
python3 chatgpt_1/m3a_extract_from_panel.py --check --output /tmp/m3a-d1-situation-library.json
cmp /tmp/m3a-d1-situation-library.json chatgpt_1/m3a-d1-situation-library-2026-08-10.json
python3 chatgpt_1/m3a_verify_golden_set.py
python3 chatgpt_1/test_m3a_golden_set.py
```

## Acceptance boundary

This bundle is **submitted, not self-accepted**. I authored it through the GitHub connector and did not execute the repository locally. The golden set is not accepted until both review lenses land.

Any future byte change to a source, script, test, or golden output requires a new manifest version, regenerated output and hashes, rerun mutation tests, and the same external reviews. Updating counts or hashes alone is forbidden.
