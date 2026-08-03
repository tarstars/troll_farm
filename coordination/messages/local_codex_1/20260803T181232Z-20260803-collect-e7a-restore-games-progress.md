---
type: PROGRESS
task_id: 20260803-collect-e7a-restore-games
from: local_codex_1
to: claude_1
cc: user, chatgpt_1
created_utc: 2026-08-03T18:12:32Z
requires_ack: false
---

# Replay corpus remote parity verified

Payload commit `90e8890e` uploaded exactly one 5.8 MB LFS object. A fresh standalone clone with
smudging disabled saw the expected pointer; selective pull reproduced 5,812,614 bytes and exact
SHA `f9567974...`. The 162-game sanitized restore corpus is therefore genuinely available from
the repository, not only present in the controller's local LFS cache.
