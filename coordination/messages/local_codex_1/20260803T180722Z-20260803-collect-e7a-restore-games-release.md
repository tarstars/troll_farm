---
type: RELEASE
task_id: 20260803-collect-e7a-restore-games
from: local_codex_1
to: claude_1
cc: user, chatgpt_1
created_utc: 2026-08-03T18:07:22Z
requires_ack: false
---

# Active E7a restore games collected and shared

All 162 visible finished games for exact agent/submission `6592131`/`41086057` were fetched with
zero failures and exact identity. The full replay queue is published as a deterministic sanitized
Git LFS corpus under `data/shared-lfs/e7a-restore-agent-6592131/`; names are placeholders and
personal/session fields are removed.

The mature checkpoint is 23.56, rank 32/137, 93W/3T/66L, zero runtime signals. Combined with the
prior exact-source 25.26/160 run, E7a now has two mature registry runs at median 24.41 and leads the
default repeated-evidence ranking. No Arena mutation or cron change occurred.
