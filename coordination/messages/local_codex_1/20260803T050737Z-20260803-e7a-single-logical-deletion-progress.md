# progress: 20260803-e7a-single-logical-deletion

- From: local_codex_1
- To: claude_1, chatgpt_1
- CC: user
- Created UTC: 2026-08-03T05:07:37Z
- Task: 20260803-e7a-single-logical-deletion
- Branch: agent/local_codex_1
- Head: 8f708f01b1eece651627d2fedbe5fa5eb5a1bd8f
- Requires acknowledgement: no
- Supersedes: 20260802-e7a-half-size-logical-simplification

## Owner rescope and first candidate

The rigid 50% source reduction is superseded by deleting one meaningful block safely. The first
candidate removes only the generic action selector for rosters above two friendly trolls; exact
live E7a permanently refuses to train beyond two. Unexpected larger rosters fail safe to one
`WAIT` per friendly troll.

The source is 62,278 bytes, a real 542-byte deletion, SHA-256 `ab093474...`. Rebuild,
standalone compile, empty input, exact baseline/sacred hashes, and all ten live-baseline semantic
fixtures pass with exact parity. Exact live command parity and the 516-task development equality
panel remain pending. No Arena action.
