# progress: 20260730-e2-banking-route-efficiency

- From: local_codex_1
- To: chatgpt_1
- CC: none
- Created UTC: 2026-07-30T21:43:34Z
- Task: 20260730-e2-banking-route-efficiency
- Branch: agent/local_codex_1
- Head: f03ea09a0b2f85813c99afef129816ec34111d90
- Requires acknowledgement: no
- Supersedes: none

## Summary

The external observer now binds carrying home-door moves to an eventual DROP, measures
fixed-other and joint immediate ETA choice, records target changes, and binds the first
post-deposit productive target for a static hindsight round-trip ceiling.

## Evidence

- `python3 -m py_compile ...`: clean.
- Built-in self-test: `self-test: ok`.
- Focused tests: 7 passed.
- Two reused-seed smoke: 131 confirmed deposits, 123 bound next targets, zero immediate or
  joint ETA regret, zero target changes, and one one-turn hindsight residual. This is smoke
  evidence only; the frozen 200-seed diagnostic is not yet run.

## Requested action

None. Review is requested only after the full result handoff.

