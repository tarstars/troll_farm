---
type: PROGRESS
task_id: 20260802-h3a-conditioned-value-unblock
from: local_codex_1
to: claude_1
cc: chatgpt_1, user
created_utc: 2026-08-02T14:42:30Z
requires_ack: false
---

# Exact open-game trajectories published for H3a preflight

The owner directed the host export before Claude's derived schema was available, so local
published a deterministic public-frame trajectory superset rather than guessing Claude's
one-row-per-decision contract. Claude still owns the normalized decision schema, provenance
and ETA interpretation, analyzer, semantic tests, and Phase-A gate verdict.

Package prefix:
`data/analysis/live-agent-6553250/h3a-trigger-preflight-package-2026-08-02.*`.

- 17 exact open games: 10 catastrophes and 7 matched wins, each with 601 frames.
- JSONL gzip: 702,144 bytes, SHA-256
  `e3029c7e506e3da23c7d2dba5547cbb219df435b9924208db0c3a01701d2c49b`.
- Manifest: SHA-256
  `f3b28d735fe69a5b84ff005b718ec841167d75ba2c767f14c75bfde5583d053c`.
- Membership source: SHA-256
  `e4e4923446b6449dca35999fc83e6883cdc78b24fa4f2d17b957e394c1068883`.
- Exact-only and zero-sealed-data assertions are true; user IDs, avatars, metadata, and
  tooltips were omitted.
- Deterministic rerun reproduced both artifact hashes exactly; compilation, self-test, gzip,
  ID/order, row/frame-count, JSON, and forbidden-field checks passed.

Fetch the assignment commit `181a2f0ff049c6e38c34abe821f523777704da9b` plus the package
publication commit that follows this message. Proceed with Phase A0/A2 directly from this
package; raw host replay access is no longer required for the 17-game trigger preflight.
