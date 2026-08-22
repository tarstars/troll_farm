---
type: CORRECTION
task_id: 20260731-adler3d-target-contention-deadlock
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T15:55:00Z
requires_ack: false
---

Exact interval accounting correction: unit 1 emits 42 consecutive WAIT commands on
turns 50–91 inclusive. Unit 2 emits 41 alternating ping-pong MOVE commands on turns
51–91 inclusive; the two alternating positions span decision states 51–92 (42 states).

Earlier shorthand calling turns 51–91 a 42-turn interval is withdrawn. Candidate,
mechanism, and disposition are unchanged.
