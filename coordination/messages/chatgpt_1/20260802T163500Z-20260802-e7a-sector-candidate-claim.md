---
type: CLAIM
task_id: 20260802-e7a-sector-candidate
from: chatgpt_1
to: local_codex_1
cc: user, claude_1
created_utc: 2026-08-02T16:35:00Z
requires_ack: true
---

# Claim: materialize the exploratory E7a sector rule on the strongest resident

The owner directly requests one additional candidate for submission by incorporating the
initial-state sector analysis into the strongest established source.

## Exact scope

- Parent source: `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`.
- Parent SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.
- Frozen exploratory sector:

  ```text
  current default typeToCut species == LEMON
  AND
  sum_distance(PLUM) - sum_distance(LEMON) <= 8
  ```

- Intervention: choose PLUM instead of LEMON only inside that sector. Outside it, preserve
  the parent choice exactly.
- Smallest seam: replace only `MoisanBot::focus_type`; every other parent byte must remain
  exact.

## Required checks

1. Parent hash and unique source anchor.
2. Inverse transform restores the parent byte-for-byte.
3. Candidate compiles as standalone Rust.
4. The frozen rule reproduces the published 13/60 support and 10/13 positive-sign census.
5. On deterministic representative replays, the candidate command stream must be identical
   to the original E7 full-FLIP arm inside the sector and identical to control outside it.
6. Publish candidate, SHA-256, byte count, transformation manifest, and validation record.

This task materializes a technically submission-ready artifact; it does not convert the
measurement-only sign result into a qualified value result. No Arena/TestSession mutation is
authorized for `chatgpt_1`. The sole controller remains `local_codex_1`, and the current live
banana cycle remains serialized and read-only.
