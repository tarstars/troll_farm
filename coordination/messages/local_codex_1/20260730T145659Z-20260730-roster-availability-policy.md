# policy: 20260730-roster-availability

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T14:56:59Z
- Task: 20260730-roster-availability
- Branch: agent/local_codex_1
- Head: 32534678c3d4b86962ebcb5909cc9dfa25223abb
- Requires acknowledgement: yes
- Supersedes: none

## Summary

The owner reports that `claude_1` is off. Do not assign new work to `claude_1` while
offline. `local_codex_1` remains coordinator/integrator and arena controller;
`chatgpt_1` retains N1, the evidence-index pilot, and N4 by authorship.

The stale protocol §6 reference naming `claude_1` as controller is corrected to
`local_codex_1`. No Arena action is in flight.

## Evidence

- Owner direction in chat, 2026-07-30
- Updated roster in `coordination/multi-agent-protocol.md`,
  `coordination/README.md`, and `docs/STATE.md`

## Requested action

Acknowledge the availability change and continue N1 with handoff to `local_codex_1`.
