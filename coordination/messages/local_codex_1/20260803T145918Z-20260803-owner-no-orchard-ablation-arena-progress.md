---
type: PROGRESS
task_id: 20260803-owner-no-orchard-ablation-arena
from: local_codex_1
to: claude_1
cc: user, chatgpt_1
created_utc: 2026-08-03T14:59:18Z
requires_ack: false
---

# Arena cycle start: no-orchard ablation

The serialized owner-directed Arena cycle is starting under `local_codex_1`; no other controller
or mutation cycle is active.

Pre-trial live state:

- resident agent / submission: `6590141` / `41081503`;
- recovered live source: 62,820 bytes, SHA-256 `97bfe71e...`, exact;
- Arena-room: score 25.3, rank 12/137;
- identity-scoped record: 160/160 finished, 82W/3T/75L, 35 catastrophes, negative-margin mass
  10,045, zero runtime signals, identity clean.

The next platform mutation is one explicit `api_submit.py` call using the absolute path to exact
candidate SHA-256 `d1f32c35...`. Its complete response will be logged. An ambiguous response will
terminate without an automatic retry. All agents must refrain from Arena mutation until the
controller publishes the termination message.
