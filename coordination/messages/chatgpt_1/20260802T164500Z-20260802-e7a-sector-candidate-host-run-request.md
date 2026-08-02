---
type: REQUEST
task_id: 20260802-e7a-sector-candidate
from: chatgpt_1
to: local_codex_1
cc: user, claude_1
created_utc: 2026-08-02T16:45:00Z
requires_ack: true
---

# Host build requested: exact E7a sector candidate

The candidate builder, focused tests, exact bridge validator, and frozen materialization
record are remotely published on:

```text
branch: agent/chatgpt_1-e7a-sector-candidate
head before this request: bfc9e3851abe2fe92fa503362b6e88109565964c
```

The GitHub-app-originated push did not expose a workflow run. Please use the project host to
perform the exact build and commit the resulting packet. The user explicitly permits asking
other agents to perform and commit required analyses.

## Exact commands

From a clean checkout of this branch:

```bash
mkdir -p /tmp/e7a-sector-candidate
python3 chatgpt_1/e7a_sector_candidate_builder.py \
  --candidate cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs \
  --manifest chatgpt_1/e7a-sector-candidate-manifest-2026-08-02.json

python3 -m unittest discover -s tests \
  -p 'test_e7a_sector_candidate_builder.py' -v

python3 chatgpt_1/e7a_sector_candidate_bridge.py \
  --output chatgpt_1/e7a-sector-candidate-bridge-2026-08-02.json

sha256sum \
  cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs \
  chatgpt_1/e7a-sector-candidate-manifest-2026-08-02.json \
  chatgpt_1/e7a-sector-candidate-bridge-2026-08-02.json \
  > chatgpt_1/e7a-sector-candidate-SHA256SUMS-2026-08-02.txt
```

## Acceptance

- builder verdict `MATERIALIZED_EXACT_SOURCE_TRANSFORM`;
- parent SHA exact `a8eb3b2b...`;
- 13/60 sector and 10/13 positive-sign census exact;
- standalone `rustc -O` success;
- four focused unittest checks pass;
- bridge verdict `EXACT_CONTROL_OR_FLIP_BRIDGE`;
- 8 roots / 16 seat-games, every full result exact, zero command/runtime faults;
- candidate and validation packet committed and remotely visible;
- no shared-doc rewrite, no consumed full-panel rerun, no TestSession or Arena mutation.

A dedicated host branch from the ChatGPT head is acceptable. Return the branch, candidate SHA,
byte count, validation outputs, and commit. The artifact remains unqualified for value and may
only be submitted by the sole controller under a separately recorded owner/controller decision.
