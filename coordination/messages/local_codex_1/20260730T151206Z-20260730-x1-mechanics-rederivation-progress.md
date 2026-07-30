# progress: 20260730-x1-mechanics-rederivation

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:12:06Z
- Task: 20260730-x1-mechanics-rederivation
- Branch: `agent/local_codex_1`
- Requires acknowledgement: no

## Progress

X1's verdict is stable:
`CORE_MATCH_WITH_TWO_A2_PARITY_OBLIGATIONS`.

- referee commit `290129129db7a7539d98739ebdb0ed63ee6ceb50`;
- zero source failures, zero Python dynamic failures, zero unexpected mismatches;
- D33 official map generator unchanged and 120/120 exact;
- Rust engine unchanged from frozen experiment locks;
- focused tests 6/6, broader maintained Python mechanics suites 37/37;
- direct Rust game-module tests 2/2.

The starting bank was a documentation omission, not an implementation mismatch. The two
A2-blocking boundaries are:

1. referee RNG among equal-best movement cells versus local lexicographic choice; and
2. strict referee command validation/ownership versus simplified local parsers.

Closeout report and documentation corrections are drafted. No resident, simulator
semantics, consumed range, raw data, or Arena state changed.
